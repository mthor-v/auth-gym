from rest_framework import serializers
from authApp.models import User
from rest_framework.response import Response

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):

        data = super().validate(attrs)

        data['name'] = self.user.name
        data['role'] = self.user.role
        data['status'] = self.user.active
        data['pay'] = self.user.payment_ok

        return data

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model   = User
        fields  = ['id','dni','name', 'last_name', 'email', 'password', 'birth', 'phone', 'other_contact', 'gender', 'role', 'active', 'payment_ok' ]
    
    def create(self, validated_data):
        userInstance = User.objects.create(**validated_data)
        return userInstance

    def customer_data(self, obj):
        user = User.objects.get(dni=obj.dni)
        return {
            'dni'       : user.dni,
            'name'      : user.name,
            'last_name' : user.last_name,
            'gender'    : user.gender,
            'email'     : user.email,
            'birth'     : user.birth,
            'phone'     : user.phone,
            'is_active' : user.active,
            'pay_ok'    : user.payment_ok
        }