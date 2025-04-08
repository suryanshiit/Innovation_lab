import paho.mqtt.client as mqtt
import pymongo
from datetime import datetime
import os 
from dotenv import load_dotenv
load_dotenv()

# MQTT Broker Details
BROKER = os.getenv("MQTT_BROKER")
TOPIC = "fire_status"

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client.fire_sensor_data  # Database name
collection = db.readings  # Collection name

# MQTT Callback function when message is received
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f"Received: {payload}")
    
    # Parse message
    try:
        data = payload.strip("{} ").split()
        sensor_data = {
            "node_id": int(data[0]),  # Extract node_id
            "sensor1": int(data[2]),
            "sensor2": int(data[4]),
            "analog_sensor": int(data[6]),
            "timestamp": datetime.utcnow()
        }
        
        # Insert into MongoDB
        collection.insert_one(sensor_data)
        print("Data inserted into MongoDB:", sensor_data)
    except Exception as e:
        print("Error parsing or inserting data:", e)

# MQTT Setup
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, 1883, 60)
mqtt_client.subscribe(TOPIC)

print("Subscribed to topic:", TOPIC)

# Start MQTT loop
mqtt_client.loop_forever()
