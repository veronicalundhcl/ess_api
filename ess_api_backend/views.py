# Create your views here.
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import TokenAuthentication
import jwt
from rest_framework.response import Response

# from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Department, Order
from .models import Product, Customer, User
from .models import Province
from .models import Cart
import logging

from .serializers import CartSerializer, OrderSerializer


def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'token': token})


def user_login(request):
    logging.error(f"LOGIN REQUEST: {request}")
    logging.error(request.POST)
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, email=email, password=password, backend='ess_api_backend.backends.auth.ESSApiBackend')
    if user is not None:
        login(request, user)
        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)},
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        token_str = token.decode('utf-8')  # convert token to string
        # Redirect to a success page.
        response = JsonResponse({'message': 'Login successful!', 'token': token_str})
        return response
    else:
        # The user is not authenticated.
        return HttpResponse("User does not exist")


def user_logout(request):
    logout(request)
    return HttpResponse('Logged out successfully.')


# TODO add JWT token validation
def authenticate_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        return user
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.DecodeError:
        raise AuthenticationFailed('Token is invalid')
    except User.DoesNotExist:
        raise AuthenticationFailed('User not found')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
def get_user_profile(request):
    try:
        email = request.POST['email']
        user = User.objects.get(email=email)
        customer = Customer.objects.get(user=user)
    except User.DoesNotExist:
        return HttpResponse("User does not exist")
    except Customer.DoesNotExist:
        return HttpResponse("Customer does not exist")

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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])
# @authentication_classes([TokenAuthentication])
def update_user_profile(request):
    try:
        email = request.user.email
        user = User.objects.get(email=email)
        customer = Customer.objects.get(user=user)
    except User.DoesNotExist:
        return HttpResponse("User does not exist")
    except Customer.DoesNotExist:
        return HttpResponse("Customer does not exist")

    # Update customer fields if they exist in request data
    if 'department' in request.data:
        customer.department = request.data['department']
    if 'contactnum' in request.data:
        customer.contactnum = request.data['contactnum']
    if 'address' in request.data:
        customer.address = request.data['address']
    if 'province' in request.data:
        customer.province = request.data['province']

    # Save updated customer fields to database
    customer.save()

    # Return updated user data in response
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
def get_product(request):
    products = Product.objects.all()
    data = {'products': list(products.values())}
    return JsonResponse(data)


def update_inventory(request):
    pass


@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
def get_products_from_cart(request):
    user = User.objects.get(email=request.user)
    customer = Customer.objects.get(user=user)
    cart_items = Cart.objects.filter(customer=customer).values()
    # serializer = CartSerializer(cart_items, many=True)
    return JsonResponse({'cart': list(cart_items)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_products_to_cart(request):
    # Get the user object from the request
    user = User.objects.get(email=request.user)

    # Find the corresponding customer object from the Customer table
    customer = get_object_or_404(Customer, user=user)

    # Get the list of products from the request data
    products = request.data.get('products')

    # Retrieve all existing cart items for the customer
    existing_cart_items = Cart.objects.filter(customer=customer)
    num_products = 0
    for product in products:
        # Get the product ID and quantity for the current product
        product_id = product.get('id')
        quantity = product.get('quantity')

        # Try to get an existing cart item with the given product and customer
        product = get_object_or_404(Product, pk=product_id)
        cart_item = existing_cart_items.filter(customer=customer, product_id=product).first()

        # If an existing cart item was found, increment its quantity
        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
        # Otherwise, create a new cart item with the given quantity
        else:
            Cart.objects.create(customer=customer, product_id=product, quantity=quantity, price=product.price)

        num_products += 1

    if num_products > 1:
        message = "Items successfully added to cart"
    else:
        message = "Item successfully added to cart"

    # Retrieve all updated cart items for the customer
    updated_cart_items = Cart.objects.filter(customer=customer)

    # Serialize the updated cart items and send them in the response
    cart_serializer = CartSerializer(updated_cart_items, many=True)

    return Response({'message': message, 'cart': cart_serializer.data})


def update_products_to_cart(request):
    pass


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_products_from_cart(request):
    # Get the user object from the request
    user = User.objects.get(email=request.user)

    # Find the corresponding customer object from the Customer table
    customer = get_object_or_404(Customer, user=user)

    # Get the list of products from the request data
    products = request.data.get('products')

    # Retrieve all existing cart items for the customer
    existing_cart_items = Cart.objects.filter(customer=customer)

    # Delete cart items if there are no products left in them
    for cart_item in existing_cart_items:
        if cart_item.quantity <= 0:
            cart_item.delete()

    # Delete products from the cart based on quantity
    num_deleted = 0
    for product in products:
        # Get the product ID and quantity for the current product
        product_id = product.get('id')
        quantity = product.get('quantity')

        # Try to get an existing cart item with the given product and customer
        product = get_object_or_404(Product, pk=product_id)
        cart_item = existing_cart_items.filter(customer=customer, product_id=product).first()

        # If an existing cart item was found, decrease its quantity
        if cart_item:
            if cart_item.quantity - quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity -= quantity
                cart_item.save()

            num_deleted += 1

    if num_deleted > 1:
        message = "Items successfully deleted from cart"
    else:
        message = "Item successfully deleted from cart"

    # Retrieve all updated cart items for the customer
    updated_cart_items = Cart.objects.filter(customer=customer)

    # Serialize the updated cart items and send them in the response
    cart_serializer = CartSerializer(updated_cart_items, many=True)

    return Response({'message': message, 'cart': cart_serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def empty_user_cart(request):
    # Get the user object from the request
    user = User.objects.get(email=request.user)

    # Find the corresponding customer object from the Customer table
    customer = get_object_or_404(Customer, user=user)

    # Retrieve all existing cart items for the customer
    cart_items = Cart.objects.filter(customer=customer)

    # Delete all existing cart items for the customer
    cart_items.delete()

    return Response({'message': 'Cart successfully emptied'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    # Get the user object from the request
    user = User.objects.get(email=request.user)

    # Find the corresponding customer object from the Customer table
    customer = get_object_or_404(Customer, user=user)

    # Retrieve all cart items for the customer
    cart_items = Cart.objects.filter(customer=customer)

    # Calculate the subtotal of the order
    subtotal = cart_items.aggregate(Sum('price'))['price__sum']

    logging.error(f'CART: {cart_items}, SUBTOTAL: {subtotal}')

    # Check that the subtotal is between 0 and 3000
    if not subtotal or subtotal <= 0:
        raise ValidationError("Cannot place an empty order")
    if subtotal > 3000:
        raise ValidationError("Cannot place an order totalling more than $3,000")

    # Create the order object with the user, subtotal, and current date
    order = Order.objects.create(
        user=customer,
        subtotal=subtotal,
        date_of_purchase=timezone.now(),
        order_status='complete'
    )

    # Add the product ids from the cart items to the order
    product_ids = [cart_item.product_id for cart_item in cart_items]
    order.product_ids = product_ids
    order.save()

    # Serialize the updated cart items and send them in the response
    cart_str = CartSerializer(cart_items, many=True).data

    # Delete all cart items for the customer
    cart_items.delete()

    # Serialize the order object and send it in the response
    order_serializer = OrderSerializer(order)

    return Response({'order': order_serializer.data, 'cart': cart_str})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    # Get the user object from the request
    user = User.objects.get(email=request.user)

    # Find the corresponding customer object from the Customer table
    customer = get_object_or_404(Customer, user=user)

    # Retrieve all orders for the customer
    orders = Order.objects.filter(user=customer)

    # Serialize the orders and send them in the response
    order_serializer = OrderSerializer(orders, many=True)

    return Response(order_serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
def get_province(request):
    provinces = Province.objects.all()
    data = {'provinces': list(provinces.values())}
    return JsonResponse(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
def get_department(request):
    departments = Department.objects.all()
    data = {'departments': list(departments.values())}
    return JsonResponse(data)
