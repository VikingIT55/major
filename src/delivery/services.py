import requests
from django.conf import settings


def search_nova_poshta_settlements(query: str, page: int = 1, limit: int = 20):
    url = "https://api.novaposhta.ua/v2.0/json/"
    payload = {
        "apiKey": settings.NOVA_POSHTA_API_KEY,
        "modelName": "Address",
        "calledMethod": "getSettlements",
        "methodProperties": {
            "FindByString": query,
            "Warehouse": 1,
            "Page": page,
            "Limit": limit,
        }
    }

    response = requests.post(url, json=payload)
    response_data = response.json()
    if not response_data.get("success"):
        raise ValueError(response_data.get("errors", ["Unknown error"]))
    return response_data["data"]

def get_warehouses_by_city_ref(city_ref: str):
    url = "https://api.novaposhta.ua/v2.0/json/"
    payload = {
        "apiKey": settings.NOVA_POSHTA_API_KEY,
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {
            "SettlementRef": city_ref
        }
    }

    response = requests.post(url, json=payload)
    data = response.json()
    if not data.get("success"):
        raise ValueError(data.get("errors", ["Unknown error"]))
    return data["data"]

def get_all_warehouse_types_dict():
    url = "https://api.novaposhta.ua/v2.0/json/"
    payload = {
        "apiKey": settings.NOVA_POSHTA_API_KEY,
        "modelName": "AddressGeneral",
        "calledMethod": "getWarehouseTypes",
        "methodProperties": {}
    }

    response = requests.post(url, json=payload)
    data = response.json()
    if not data.get("success"):
        raise ValueError(data.get("errors", ["Unknown error"]))

    return {
        item["Ref"]: item["Description"]
        for item in data["data"]
    }
