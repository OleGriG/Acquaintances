from rest_framework import serializers
from .models import User


class UserRegistrSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name',
                  'sex', 'password', 'password2', 'avatar']

    def save(self, *args, **kwargs):
        data = self.validated_data.copy()
        password = data.pop('password')
        password2 = data.pop('password2')
        if password != password2:
            raise serializers.ValidationError('passwords are not equal!')
        user = User.objects.create(**data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
