import smtplib
import paho.mqtt.client as mqtt
import pymongo
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# Email Configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = "suryansh16103@gmail.com"
PASSWORD = os.getenv("EMAIL_PASSWORD")  # Use an app password for Gmail

# Fire detection thresholds
ANALOG_THRESHOLD = 400  # Change this based on sensor calibration

# Track last time email was sent
last_email_time = datetime.min  # Initialize to a time far in the past

def send_email_alert(sensor_data):
    """Send an email alert when fire is detected."""
    subject = "🔥 Fire Alert! Immediate Attention Needed!"
    body = f"""
    Fire detected at Node {sensor_data['node_id']}!
    
    Sensor Readings:
    - Sensor1: {sensor_data['sensor1']}
    - Sensor2: {sensor_data['sensor2']}
    - Analog Sensor: {sensor_data['analog_sensor']}
    
    Timestamp: {sensor_data['timestamp']}
    
    Please take immediate action!
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure connection
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("🔥 Fire alert email sent successfully!")
    except Exception as e:
        print("❌ Error sending email:", e)

def on_message(client, userdata, msg):
    """Callback function when an MQTT message is received."""
    global last_email_time

    payload = msg.payload.decode("utf-8")
    print(f"📩 Received MQTT Message: {payload}")
    
    try:
        data = payload.strip("{} ").split()
        sensor_data = {
            "node_id": int(data[0]),
            "sensor1": int(data[2]),
            "sensor2": int(data[4]),
            "analog_sensor": int(data[6]),
            "timestamp": datetime.utcnow()
        }

        # Insert into MongoDB
        collection.insert_one(sensor_data)
        print("✅ Data inserted into MongoDB:", sensor_data)

        # Check for fire detection
        fire_detected = (
            sensor_data["sensor1"] == 1 or
            sensor_data["sensor2"] == 1 or
            sensor_data["analog_sensor"] > ANALOG_THRESHOLD
        )

        if fire_detected:
            print("🚨 Fire detected!")

            # Only send email if 60 seconds have passed
            if datetime.utcnow() - last_email_time >= timedelta(minutes=1):
                send_email_alert(sensor_data)
                last_email_time = datetime.utcnow()
            else:
                print("⏳ Email alert skipped to avoid spamming.")
        else:
            print("🟢 No fire detected.")
    
    except Exception as e:
        print("❌ Error parsing or inserting data:", e)

# MQTT Setup
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, 1883, 60)
mqtt_client.subscribe(TOPIC)

print(f"📡 Subscribed to MQTT topic: {TOPIC}")
mqtt_client.loop_forever()
