from rest_framework import serializers


class ProductItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    article = serializers.CharField(max_length=100)
    number_of_items = serializers.IntegerField(min_value=1)
    price_with_discount = serializers.IntegerField(min_value=1)


class CreateInvoiceInSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    last_name = serializers.CharField(max_length=128)
    amount = serializers.IntegerField(min_value=1)
    full_amount = serializers.IntegerField(min_value=1)
    ccy = serializers.IntegerField(required=False, default=980)  # 980 = UAH
    phone = serializers.CharField(min_length=10, max_length=20)
    telegram_name = serializers.CharField(max_length=64, required=False, allow_blank=True)
    delivery_method = serializers.ChoiceField(choices=["pickup", "nova_poshta"], default="pickup")
    settlement = serializers.CharField(max_length=128, required=False, allow_blank=True)
    warehouse = serializers.CharField(max_length=64, required=False, allow_blank=True)
    comment = serializers.CharField(max_length=512, required=False, allow_blank=True)
    payment_option = serializers.ChoiceField(choices=["full", "partial"], default="full")
    products = ProductItemSerializer(many=True, required=True)
    promocode = serializers.CharField(max_length=64, required=False, allow_blank=True)

    def validate(self, attrs):
        delivery = attrs.get("delivery_method")
        settlement = (attrs.get("settlement") or "").strip()
        warehouse = (attrs.get("warehouse") or "").strip()
        payment_option = attrs.get("payment_option")

        if payment_option not in ["full", "partial"]:
            raise serializers.ValidationError({"payment_option": "Invalid payment option."})
    

        if delivery == "nova_poshta":
            if not settlement:
                raise serializers.ValidationError({"settlement": "This field is required for nova_poshta delivery."})
            if not warehouse:
                raise serializers.ValidationError({"departwarehousement": "This field is required for nova_poshta delivery."})
        elif delivery == "pickup":
            attrs["settlement"] = ""
            attrs["warehouse"] = ""
        else:
            raise serializers.ValidationError({"delivery_method": "Invalid delivery method."})
            
        # Validate phone number format
        phone = attrs.get("phone", "")
        if 9 > len(phone) > 20:
            raise serializers.ValidationError({"phone": "Phone number must be between 9-20 digits."})

        return attrs


class CreateInvoiceOutSerializer(serializers.Serializer):
    invoice_id = serializers.CharField(max_length=100)
    page_url = serializers.URLField()
    reference = serializers.CharField(max_length=10)  


class InvoiceStatusSerializer(serializers.Serializer):
    invoice_id = serializers.CharField()
    status = serializers.CharField()
    amount = serializers.IntegerField(required=False)
    ccy = serializers.IntegerField(required=False)
    reference = serializers.CharField(required=False)
