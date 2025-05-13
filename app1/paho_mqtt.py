import time
import paho.mqtt.client as mqtt
from django.http import JsonResponse
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
        client.subscribe(MQTT_TOPIC)  # Subscribe to the topic
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect. Code: {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')  # Decode the MQTT message payload
        print(f"Storing Value: {payload}")

        try:
            # Convert payload to float (assuming it's a numeric value)
            base_value = float(payload)
        except ValueError:
            print("Invalid payload: Not a number")
            return

        # Get the last record from the database
        last_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()

        if not last_entry or float(last_entry.remaining_value or 0) == 0:
            # If no last entry or remaining value is zero, create a new cycle.
            print("Remaining value is zero or no previous data, starting a new cycle.")

            # Insert a new cycle row to start fresh
            Pilot_Feedtray.objects.create(
                base_value=str(base_value),
                intial_value=str(base_value),  # Set initial value
                remaining_value=str(base_value),  
                cycle_count="0",  
                cycle_value="0"  
            )

            print(f"New cycle created with base value: {base_value}")
            return JsonResponse({
                "message": "New cycle header row created.",
                "base_value": base_value
            })

        else:
            print(f"Last entry's remaining value: {last_entry.remaining_value}")
            print(f"Cycle is still active, no action taken.")
            return

    except Exception as e:
        print(f"Error processing message: {e}")

# MQTT connection starter
def mqtt_connect():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # Connect to the MQTT broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Failed to connect to broker: {e}")
        return

    # Start the loop to receive messages
    client.loop_start()

    try:
        while True:
            time.sleep(1)  
    except KeyboardInterrupt:
        print("Stopped by user.")
        client.loop_stop()
        client.disconnect()
