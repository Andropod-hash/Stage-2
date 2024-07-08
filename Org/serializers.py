from rest_framework import serializers
from .models import CustomUser, Organization



class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['orgId', 'name', 'description']
        extra_kwargs = {"orgId": {"read_only": True}}

class AddUserToOrganizationSerializer(serializers.Serializer):
    userId = serializers.UUIDField(required=True, error_messages={"required": "userId is required"})

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) 

    class Meta:
        model = CustomUser
        fields = ['userId', 'firstName', 'lastName', 'email', 'password', 'phone']
        extra_kwargs = {
            "userId": {"read_only":True},
            "firstName": {"error_messages":{"required":"First name is required"}},
            "lastName": {"error_messages":{"required":"Last name is required"}},
            "password": {"error_messages":{"required":"Password is required"}},
            "phone": {"error_messages":{"required":"Phone number is required"}},
            "email": {"error_messages":{"required":"Email address is required"}},
        }
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address is already in use")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create(
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            email=validated_data['email'],
            phone=validated_data.get('phone', '')
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)