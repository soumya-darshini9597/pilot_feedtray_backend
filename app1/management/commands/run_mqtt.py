from django.core.management.base import BaseCommand
from app1.paho_mqtt import mqtt_connect

class Command(BaseCommand):
    help = 'Starts the MQTT subscriber'

    def handle(self, *args, **kwargs):
        print("Starting MQTT Subscriber...")
        mqtt_connect()
