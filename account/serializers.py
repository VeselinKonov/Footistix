from rest_framework import serializers
from django.contrib.auth import authenticate
from account.models import User, Profile
from django.contrib.auth.hashers import make_password


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        # Take username and password from request
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs
   

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    email = serializers.EmailField(
        label="Email",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
        
    )
    

    def create(self, attrs):
        # Take username and password from request
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        attrs['password'] = make_password(attrs.get('password'))

        if username and email and password:
            # Try to authenticate the user using Django auth framework.
            try:
                user = User.objects.create(**attrs)
                Profile.objects.create(user=user)
            except:
                msg = 'This email is already used.'
                raise serializers.ValidationError(msg, code='registration')
            return user
        #     user = authenticate(request=self.context.get('request'),
        #                         username=username, password=password)
        #     if not user:
        #         # If we don't have a regular user, raise a ValidationError
        #         msg = 'Access denied: wrong username or password.'
        #         raise serializers.ValidationError(msg, code='authorization')
        # else:
        #     msg = 'Both "username" and "password" are required.'
        #     raise serializers.ValidationError(msg, code='authorization')
        # # We have a valid user, put it in the serializer's validated_data.
        # # It will be used in the view.
        # attrs['user'] = user
        # return attrs
    

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]
    