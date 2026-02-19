from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import ValidationError
import re

from users.constants import Role

User = get_user_model()

class PasswordValidator:
    min_length = 8
    require_digit = True
    require_uppercase = True
    require_lowercase = True
    require_special_char = True
    
    def __call__(self, value):
        errors = []
        
        if len(value) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long.")
        
        if self.require_digit and not re.search(r'\d', value):
            errors.append("Password must contain at least 1 digit.")
        
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            errors.append("Password must contain at least 1 uppercase letter.")
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            errors.append("Password must contain at least 1 lowercase letter.")
        
        if self.require_special_char and not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?]', value):
            errors.append("Password must contain at least 1 special character.")
        
        if errors:
            raise ValidationError(errors)
        
        return value

password_validator = PasswordValidator()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True, validators=[password_validator])

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "role"]
        read_only_fields = ["email"]

    def validate(self, attrs):
        attrs["password"] = make_password(attrs["password"])
        if self.instance is None:
            attrs["role"] = Role.USER
        else:
            attrs["role"] = self.instance.role

        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True, validators=[password_validator])

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "role"]
        read_only_fields = ["role"]

    def validate(self, attrs):
        attrs["password"] = make_password(attrs["password"])
        attrs["role"] = Role.MANAGER

        return attrs
