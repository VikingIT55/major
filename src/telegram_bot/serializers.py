from rest_framework import serializers


class CooperationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    phone = serializers.CharField(max_length=20)

class SupportSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    phone = serializers.CharField(max_length=20)
    question = serializers.CharField(max_length=500)