import pytest
from unittest.mock import Mock
from django.contrib.auth import get_user_model


@pytest.fixture
def mocker():
    return Mock()


@pytest.fixture
def user():
    email = "vlund@hcl.com"
    password = "password"
    user = get_user_model().objects.create_user(email=email, password=password)
    return user
