from rest_framework import viewsets

from products.permissions import RoleIsAdmin, RoleIsManager, RoleIsUser
from partners.models import PartnerLocation
from partners.serializers import PartnerLocationSerializer


class PartnerLocationViewSet(viewsets.ModelViewSet):
    queryset = PartnerLocation.objects.all()
    serializer_class = PartnerLocationSerializer
    permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]
    filterset_fields = ["id"]