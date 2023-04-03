from django.core.management.base import BaseCommand
import os
import sys

# Add the parent directory of ess_api_backend to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'kafka_modules')))


# Import the consume_orders function from the consumers module
from kafka_modules.consumers import consume_orders


class Command(BaseCommand):
    help = 'Starts the Kafka consumer for processing orders'

    def handle(self, *args, **options):
        consume_orders()
