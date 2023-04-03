from rest_framework import serializers
from .models import Cart, Order, Product, OrderProduct, Customer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'product', 'quantity', 'price']


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderProduct
        fields = ('id', 'product', 'quantity', 'price')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['user', 'firstname', 'lastname', 'dob', 'department', 'role', 'contactnum', 'address', 'province',
                  'country']


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    order_products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_status', 'subtotal', 'date_of_purchase', 'order_products')



