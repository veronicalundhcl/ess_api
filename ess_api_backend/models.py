import uuid
from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.

# class User(models.Model):
#     userId = models.CharField(max_length=255, unique=True, default="")
#     password = models.CharField(max_length=255)

class UserManager(BaseUserManager):
    def create_user(self, userId, password=None, **extra_fields):
        """
        Creates and saves a new user with the given userId and password.
        """
        if not userId:
            raise ValueError('The userId field must be set')
        user = self.model(userId=userId, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, userId, password):
        """
        Creates and saves a new superuser with the given userId and password.
        """
        user = self.create_user(userId, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, default="")
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='ess_api_backend_users'  # add a related_name here
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='ess_api_backend_users'  # add a related_name here
    )


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True, default=0, editable=False)
    firstname = models.CharField(max_length=50, default="")
    lastname = models.CharField(max_length=50, default="")
    dob = models.DateField(null=True)
    department = models.CharField(max_length=50, null=True)
    role = models.CharField(max_length=50, default="")
    contactnum = models.CharField(max_length=15, null=True)
    address = models.CharField(max_length=100, null=True)
    province = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, default="")

    objects = models.Manager()


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    img = models.TextField(null=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    category = models.TextField(default='Uncategorized')
    reviews = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)], default=1)
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    link = models.TextField(null=True)

    objects = models.Manager()


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='id')
    quantity = models.IntegerField()
    price = models.IntegerField()


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    date_of_purchase = models.DateField(null=True)


class Province(models.Model):
    id = models.CharField(max_length=2, primary_key=True)
    value = models.CharField(max_length=255, null=True)


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=255, null=True)
