from rest_framework import serializers
from django.utils.translation import get_language

from users.constants import Role
from partners.models import PartnerLocation


class PartnerLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerLocation
        fields = [
            "id",
            "name_uk",
            "name_en",
            "addres_uk",
            "addres_en",
            "work_schedule_weekdays",
            "work_schedule_weekends",
            "google_maps_link",
            "longitude",
            "latitude",
        ]
        read_only_fields = ["id"]   

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request", None)
        lang_code = get_language()
        if lang_code == "uk":
            representation["name"] = representation["name_uk"]
            representation["addres"] = representation["addres_uk"]
        else:
            representation["name"] = representation["name_en"]
            representation["addres"] = representation["addres_en"]
        if (
            request
            and request.user.is_authenticated
            and request.user.role in [Role.ADMIN, Role.MANAGER]
        ):
            pass
        else:
            representation.pop("name_uk", None)
            representation.pop("name_en", None)
            representation.pop("addres_uk", None)
            representation.pop("addres_en", None)

        return representation



