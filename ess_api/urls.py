"""ess_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin

from ess_api_backend.views import (
    user_login,
    user_logout,
    authenticate_token,
    get_user_profile,
    update_user_profile,
    get_product,
    update_inventory,
    get_products_from_cart,
    add_products_to_cart,
    update_products_to_cart,
    delete_products_from_cart,
    empty_user_cart,
    place_order,
    get_province,
    get_department
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login/', user_login, name='user_login'),
    path('auth/logout/', user_logout, name='user_logout'),
    path('auth/token/', authenticate_token, name='authenticate_token'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('profile/update/', update_user_profile, name='update_user_profile'),
    path('product/', get_product, name='get_product'),
    path('product/update/', update_inventory, name='update_inventory'),
    path('cart/', get_products_from_cart, name='get_products_from_cart'),
    path('cart/add/', add_products_to_cart, name='add_products_to_cart'),
    path('cart/update/', update_products_to_cart, name='update_products_to_cart'),
    path('cart/delete/', delete_products_from_cart, name='delete_products_from_cart'),
    path('cart/empty/', empty_user_cart, name='empty_user_cart'),
    path('order/place/', place_order, name='place_order'),
    path('province/', get_province, name='get_province'),
    path('department/', get_department, name='get_department'),
]
