from rest_framework import serializers
from ..models import User

from rest_framework import serializers
from ..models import User

class AuthSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    passwordConfirmation = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'passwordConfirmation']

    def validate(self, data):
        if data['password'] != data['passwordConfirmation']:
            raise serializers.ValidationError('Passwords do not match.')
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('passwordConfirmation')
        return User.objects.create_user(**validated_data)
    

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']