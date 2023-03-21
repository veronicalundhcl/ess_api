# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods

from .models import Product, Customer, User
from .models import Province
from .models import Department

import logging


def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'token': token})


@csrf_exempt
@ensure_csrf_cookie
def user_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        response = JsonResponse({'message': 'Login successful!'})
        response['X-CSRFToken'] = get_token(request)
        return response
    else:
        # The user is not authenticated.
        return HttpResponse("User does not exist")


def user_logout(request):
    logout(request)
    return HttpResponse('Logged out successfully.')


def authenticate_token(request):
    pass


@require_http_methods(['POST'])
def get_user_profile(request):
    try:
        username = request.POST['username']
        user = User.objects.get(username=username)
        customer = Customer.objects.get(user=user)
    except (User.DoesNotExist, Customer.DoesNotExist):
        return HttpResponse("User does not exist")

    user_data = {
        'first_name': customer.firstname,
        'last_name': customer.lastname,
        'email': user.email,
        'dob': customer.dob,
        'department': customer.department,
        'role': customer.role,
        'contactnum': customer.contactnum,
        'address': customer.address,
        'province': customer.province,
        'country': customer.country
    }

    return JsonResponse(user_data)


def update_user_profile(request):
    pass


@require_http_methods(['GET'])
def get_product(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this resource.")
    products = Product.objects.all()
    data = {'products': list(products.values())}
    return JsonResponse(data)


def update_inventory(request):
    pass


def get_products_from_cart(request):
    pass


def add_products_to_cart(request):
    pass


def update_products_to_cart(request):
    pass


def delete_products_from_cart(request):
    pass


def empty_user_cart(request):
    pass


def place_order(request):
    pass


def get_province(request):
    provinces = Province.objects.all()
    data = {'provinces': list(provinces.values())}
    return JsonResponse(data)


def get_department(request):
    departments = Department.objects.all()
    data = {'departments': list(departments.values())}
    return JsonResponse(data)
