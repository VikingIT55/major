from base64 import b64decode
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
import requests
from typing import Dict, Any, Optional
from django.conf import settings

class MonoClient:
    CREATE_PATH = "/api/merchant/invoice/create"
    STATUS_PATH = "/api/merchant/invoice/status"

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 15):
        conf = getattr(settings, "MONOBANK", {})
        self.base_url = (base_url or conf.get("BASE_URL", "https://api.monobank.ua")).rstrip("/")
        self.token = token or conf.get("TOKEN", "")
        self.timeout = conf.get("TIMEOUT", timeout)
        self.session = requests.Session()
        self.session.headers.update({
            "X-Token": self.token,
            "Content-Type": "application/json",
        })

    def create_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{self.CREATE_PATH}"
        resp = self.session.post(url, json=data, timeout=self.timeout)
        try:
            js = resp.json()
        except Exception:
            js = {"text": resp.text}
        return {"status_code": resp.status_code, "json": js}

    def get_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}{self.STATUS_PATH}"
        resp = self.session.get(url, params={"invoiceId": invoice_id}, timeout=self.timeout)

        try:
            js = resp.json()
        except Exception:
            js = {"text": resp.text}
        return {"status_code": resp.status_code, "json": js}

    @staticmethod
    def verify_webhook_signature(raw_body: bytes, header_x_sign: str) -> bool:
        pub_pem = getattr(settings, "MONOBANK", {}).get("WEBHOOK_PUBLIC_KEY", "")
        if not pub_pem:
            raise ValueError("Monobank public key is not configured in settings.MONOBANK['WEBHOOK_PUBLIC_KEY']")

        try:
            signature = b64decode(header_x_sign)
            public_key = serialization.load_pem_public_key(pub_pem.encode("utf-8"))
            public_key.verify(signature, raw_body, ec.ECDSA(hashes.SHA256()))
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False