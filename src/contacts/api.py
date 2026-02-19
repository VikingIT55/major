from rest_framework import viewsets

from contacts.models import Contact
from contacts.serializers import ContactSerializer 
from contacts.permissions import ContactPermission



class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [ContactPermission]
