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

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255, unique=True, default="")
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

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

    # TODO implement encryption for storing passwords
    def check_password(self, raw_password):
        return self.password == raw_password


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
    inventory = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    objects = models.Manager()


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='id')
    quantity = models.IntegerField()
    price = models.IntegerField()

    objects = models.Manager()


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=50, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=2)
    date_of_purchase = models.DateTimeField(null=True)

    objects = models.Manager()


class OrderProduct(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)

    objects = models.Manager()


class Province(models.Model):
    id = models.CharField(max_length=2, primary_key=True)
    value = models.CharField(max_length=255, null=True)


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=255, null=True)
