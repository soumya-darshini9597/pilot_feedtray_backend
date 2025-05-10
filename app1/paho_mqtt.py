import time
import json
import paho.mqtt.client as mqtt
from datetime import date
from django.utils.timezone import now
from .models import Pilot_Feedtray  

# MQTT Configuration
MQTT_BROKER = 'mqttbroker.bc-pl.com'
MQTT_PORT = 1883  
MQTT_TOPIC = 'publish/2'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'Bfl@2025'

# Callback when connected to broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect. Code: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')  
        print(f"Received payload: {payload}")

        try:
            base_value = float(payload)
        except ValueError:
            print("Invalid payload: Not a number")
            return

        # Get last record
        last_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()

        # Check if we need to start a new cycle
        if not last_entry or float(last_entry.remaining_value or last_entry.base_value) == 0:
            # New base cycle – store with cycle_count = 0
            Pilot_Feedtray.objects.create(
                base_value=str(base_value),
                intial_value=str(base_value),
                remaining_value=str(base_value),
                cycle_count='0'
            )
            print(f"Stored new cycle with cycle_count = 0 and base_value = {base_value}")
        else:
            print(f"Skipped storing. Previous remaining/base value not zero: {last_entry.remaining_value or last_entry.base_value}")

    except Exception as e:
        print(f"Error processing message: {e}")


# MQTT connection starter
def mqtt_connect():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Failed to connect to broker: {e}")
        return

    client.loop_start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped by user.")
        client.loop_stop()
        client.disconnect()
