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

# Callback when message is received
def on_message(client, userdata, msg):
    try:
        today = date.today()

        # # Delete entries not from today (using timestamp field)
        # Pilot_Feedtray.objects.exclude(timestamp__date=today).delete()

        payload = msg.payload.decode('utf-8')
        base_value = (payload)
        print(f"Storing: {base_value}")

        # Save to database
        Pilot_Feedtray.objects.create(base_value)

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
