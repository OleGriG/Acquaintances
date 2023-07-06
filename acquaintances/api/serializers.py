from rest_framework import serializers
from .models import User


class UserRegistrSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'sex', 'password', 'password2', 'avatar']

    def save(self, *args, **kwargs):
        user = User(email=self.validated_data['email'])
        user.sex = self.validated_data['sex']
        user.first_name = self.validated_data['first_name']
        user.last_name = self.validated_data['last_name']
        user.avatar = self.validated_data['avatar']
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError('passwords are not equal!')
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
