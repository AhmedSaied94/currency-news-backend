from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.exceptions import AuthenticationFailed
from currency.api.v1.serializers import CurrencySerializer
from django_countries.serializers import CountryFieldMixin

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'password',
            'fullname',
            'profile_pic',
            'join_date',
            'country',
            'home_currency',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):

        user = User(
            email=self.validated_data.get('email'),
            username=self.validated_data.get('username'),
            fullname=self.validated_data.get('fullname'),
            profile_pic=self.validated_data.get('profile_pic'),
            country=self.validated_data.get('country'),
            home_currency=self.validated_data.get('home_currency'),
            base_currency=self.validated_data.get('base_currency')
        )
        try:
            validate_password(self.validated_data.get('password'), user)
        except Exception as e:
            raise serializers.ValidationError({'password': [e]})

        user.set_password(self.validated_data.get('password'))
        user.save()
        return user


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('check old password again')

    def validate_new_password(self, value):
        try:
            validate_password(value, self.context['request'].user)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class resetPasswordCompleteSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    uid64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    class Meta:
        fields = ['password', 'uid64', 'token']

    def validate_password(self, value):
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(str(e), code=400)
        return value

    def save(self, **kwargs):

        uid64 = self.validated_data['uid64']
        token = self.validated_data['token']
        id = smart_str(urlsafe_base64_decode(uid64))
        user = User.objects.get(id=id)
        print(user, token)

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed(
                detail='link has been expired', code=401)

        user.set_password(self.validated_data['password'])
        user.save()
        return user


class UserDataSerializer(CountryFieldMixin, serializers.ModelSerializer):

    favorites = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'fullname',
            'profile_pic',
            'join_date',
            'country',
            'home_currency',
            'favorites',
        ]

    def get_favorites(self, obj):
        if hasattr(obj, 'favorites'):
            return CurrencySerializer(
                instance=obj.favorites.currencies.all(),
                many=True
            ).data
