# Create your views here.
import json
from datetime import datetime, timedelta

import django
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
import jwt
from rest_framework.response import Response

from kafka_modules.producers import send_order
# from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Department, Order, OrderProduct
from .models import Product, Customer, User
from .models import Province
from .models import Cart
import logging

from .serializers import CartSerializer, OrderSerializer

from django.http import HttpResponse
from django.middleware.csrf import get_token

from django.http import JsonResponse

# def get_csrf_token(request):
#     response = JsonResponse({'csrftoken': get_token(request)})
#     csrftoken = json.loads(response.content).get('csrftoken')
#     logging.error(f'TOKEN ISSUED BY GET_TOKEN(REQUEST): {csrftoken}')
#     response['Access-Control-Allow-Credentials'] = 'true'
#     response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
#     return response
from django.http import JsonResponse


def get_csrf_token(request):
    csrf_token = django.middleware.csrf.get_token(request)
    logging.error(f"CSRF TOKEN: {csrf_token}")
    response = JsonResponse({'csrf_token': csrf_token})
    response.set_cookie('csrftoken', csrf_token, httponly=True)
    return response


from django.http import JsonResponse


def user_login(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')

    user = authenticate(request, email=email, password=password, backend='ess_api_backend.backends.auth.ESSApiBackend')
    if user is not None:
        login(request, user)
        auth_token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)},
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        auth_token_str = auth_token.decode('utf-8')
        response_data = {'status': 'success', 'message': 'Login successful!', 'auth_token': auth_token_str}
        return JsonResponse(response_data, status=200)
    else:
        # The user is not authenticated.
        response_data = {'status': 'error', 'message': 'User does not exist'}
        return JsonResponse(response_data, status=401)


def user_logout(request):
    logout(request)
    response = JsonResponse({'message': 'Logged out successfully'})
    return response


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
        response = JsonResponse({'error': 'User does not exist'})
        return response
    except Customer.DoesNotExist:
        response = JsonResponse({'error': 'Customer does not exist'})
        return response

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
        response = JsonResponse({'error': 'User does not exist'})
        return response
    except Customer.DoesNotExist:
        response = JsonResponse({'error': 'Customer does not exist'})
        return response

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
    logging.error(f"REQUEST DATA {request.data}")
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
            Cart.objects.create(customer=customer, product_id=product.id, quantity=quantity, price=product.price)

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

    if num_deleted == 1:
        message = "Item successfully deleted from cart"
    else:
        message = "Items successfully deleted from cart"

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


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def place_order(request):
#     # Get the user object from the request
#     user = User.objects.get(email=request.user)
#
#     # Find the corresponding customer object from the Customer table
#     customer = get_object_or_404(Customer, user=user)
#
#     # Retrieve all cart items for the customer
#     cart_items = Cart.objects.filter(customer=customer)
#
#     # Calculate the subtotal of the order
#     subtotal = cart_items.aggregate(Sum('price'))['price__sum']
#
#     logging.error(f'CART: {cart_items}, SUBTOTAL: {subtotal}')
#
#     # Check that the subtotal is between 0 and 3000
#     if not subtotal or subtotal <= 0:
#         # raise ValidationError("Cannot place an empty order")
#         return Response({'error': 'Cannot place an empty order'})
#     if subtotal > 3000:
#         # raise ValidationError("Cannot place an order totalling more than $3,000")
#         return Response({'error': 'Cannot place an order totalling more than $3,000'})
#
#     # Create the order object with the user, subtotal, and current date
#     order = Order.objects.create(
#         user=customer,
#         subtotal=subtotal,
#         date_of_purchase=timezone.now(),
#         order_status='complete'
#     )
#
#     # Add the product ids from the cart items to the order
#     product_ids = [cart_item.product_id for cart_item in cart_items]
#     order.product_ids = product_ids
#     order.save()
#
#     # Serialize the updated cart items and send them in the response
#     cart_str = CartSerializer(cart_items, many=True).data
#
#     # Delete all cart items for the customer
#     cart_items.delete()
#
#     # Serialize the order object and send it in the response
#     order_serializer = OrderSerializer(order)
#
#     return Response({'order': order_serializer.data, 'cart': cart_str})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    # Get the customer object from the request
    customer = get_object_or_404(Customer, user=request.user)

    # Retrieve all cart items for the customer
    cart_items = Cart.objects.filter(customer=customer)

    # Calculate the subtotal of the order
    subtotal = cart_items.aggregate(Sum('price'))['price__sum']

    logging.error(f'CART: {cart_items}, SUBTOTAL: {subtotal}')

    # Check that the subtotal is between 0 and 3000
    if not subtotal or subtotal <= 0:
        # raise ValidationError("Cannot place an empty order")
        return Response({'error': 'Cannot place an empty order'})
    if subtotal > 3000:
        # raise ValidationError("Cannot place an order totalling more than $3,000")
        return Response({'error': 'Cannot place an order totalling more than $3,000'})

    # Create the order object with the customer, subtotal, and current date
    order = Order.objects.create(
        customer=customer,
        subtotal=subtotal,
        date_of_purchase=timezone.now(),
        order_status='complete'
    )

    # Create OrderProduct objects for each cart item
    for cart_item in cart_items:
        OrderProduct.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.price
        )

    # Delete all cart items for the customer
    cart_items.delete()

    # Serialize the order object and send it in the response
    order_serializer = OrderSerializer(order)

    send_order(order_serializer.data)

    return Response({'order': order_serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_inventory(request):
    if request.method == 'POST':
        try:
            # Get the products and inventory updates from the request data
            products = request.data.get('products')

            # Loop through the products and update the inventory amounts in the database
            for product in products:
                product_id = product['id']
                inventory = product['inventory']
                try:
                    product = Product.objects.get(pk=product_id)
                    product.inventory = inventory
                    product.save()
                except Product.DoesNotExist:
                    pass

            # Return a success response
            response = {'status': 'success'}
            return JsonResponse(response)
        except Exception as e:
            # Return an error response if something goes wrong
            response = {'status': 'error', 'message': str(e)}
            return JsonResponse(response, status=400)
    else:
        # Return an error response for non-POST requests
        response = {'status': 'error', 'message': 'Invalid request method'}
        return JsonResponse(response, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    # Get the user object from the request
    user = User.objects.get(email=request.user)

    # Find the corresponding customer object from the Customer table
    customer = get_object_or_404(Customer, user=user)

    # Retrieve all orders for the customer
    orders = Order.objects.filter(customer=customer)

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
