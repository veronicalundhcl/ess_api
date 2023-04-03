from ess_api_backend.models import Product
from kafka import KafkaConsumer
from json import loads


def consume_orders():
    consumer = KafkaConsumer(
        'orders',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group',
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )

    for message in consumer:
        order_data = message.value
        update_inventory(order_data)


def update_inventory(order_data):
    order_products = order_data['order_products']
    for order_product in order_products:
        product_id = order_product['product']['id']
        quantity = order_product['quantity']
        product = Product.objects.get(id=product_id)
        product.inventory -= quantity
        product.save()
