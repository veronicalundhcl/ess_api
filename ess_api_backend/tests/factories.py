import uuid

import pytest
from django.contrib.auth import get_user_model

from ..models import Customer, Product, Cart, Order, OrderProduct, Province, Department


@pytest.fixture
def user_factory(db):
    def factory(**kwargs):
        email = kwargs.pop('email', None)
        password = kwargs.pop('password', None)

        if not email:
            email = f'{uuid.uuid4()}@example.com'

        if not password:
            password = 'password123'

        return get_user_model().objects.create_user(email=email, password=password, **kwargs)

    return factory


@pytest.fixture
def customer_factory(db, user_factory):
    def factory(**kwargs):
        user = kwargs.pop('user', None)

        if not user:
            user = user_factory()

        return Customer.objects.create(user=user, **kwargs)

    return factory


@pytest.fixture
def product_factory(db):
    def factory(**kwargs):
        return Product.objects.create(**kwargs)

    return factory


@pytest.fixture
def cart_factory(db, customer_factory, product_factory):
    def factory(**kwargs):
        customer = kwargs.pop('customer', None)
        product = kwargs.pop('product', None)

        if not customer:
            customer = customer_factory()

        if not product:
            product = product_factory()

        return Cart.objects.create(customer=customer, product=product, **kwargs)

    return factory


@pytest.fixture
def order_factory(db, customer_factory):
    def factory(**kwargs):
        customer = kwargs.pop('customer', None)

        if not customer:
            customer = customer_factory()

        return Order.objects.create(customer=customer, **kwargs)

    return factory


@pytest.fixture
def order_product_factory(db, order_factory, product_factory):
    def factory(**kwargs):
        order = kwargs.pop('order', None)
        product = kwargs.pop('product', None)

        if not order:
            order = order_factory()

        if not product:
            product = product_factory()

        return OrderProduct.objects.create(order=order, product=product, **kwargs)

    return factory


@pytest.fixture
def province_factory(db):
    def factory(**kwargs):
        return Province.objects.create(**kwargs)

    return factory


@pytest.fixture
def department_factory(db):
    def factory(**kwargs):
        return Department.objects.create(**kwargs)

    return factory
