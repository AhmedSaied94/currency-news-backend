from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.apps import apps
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django_countries.fields import CountryField
from currency.models import *
# Create your models here.


class UserProfileManager(BaseUserManager):

    def create_user(self, email, username, password=None, **kwargs):
        if not email:
            raise ValueError('You must enter an email address')
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **kwargs):
        user = self.create_user(email, username, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):

    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(
        max_length=255, unique=True, validators=[username_validator])
    fullname = models.CharField(max_length=255)
    join_date = models.DateTimeField(default=timezone.now)
    profile_pic = models.ImageField(
        upload_to='account/profile_pics', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    country = CountryField(null=True, blank=True)
    home_currency = models.ForeignKey(
        Currency, related_name='users', on_delete=models.SET_NULL, null=True)
    base_currency = models.ForeignKey(
        Currency, related_name='base_users', on_delete=models.SET_NULL, null=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_name(self):
        return self.fullname

    def __str__(self):
        return self.username
