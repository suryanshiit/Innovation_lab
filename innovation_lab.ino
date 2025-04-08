#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define SAMPLE_SIZE 100
int analogSamples[SAMPLE_SIZE];
int sampleIndex = 0;
bool bufferFilled = false;

// WiFi Credentials
const char* ssid = "prrockzedWifi";
const char* password = "yothereyes";

// MQTT Broker Settings
const char* broker = "3.109.19.112";
const char* topic = "fire_status";

int node_id = 1;

// Define Sensor Pins
#define SENSOR1 5    // GPIO5 (D1) - Digital Sensor 1
#define SENSOR2 4    // GPIO4 (D2) - Digital Sensor 2
#define ANALOG_SENSOR A0  // A0 - Analog Sensor
#define LED 0        // GPIO0 (D3) - LED

WiFiClient espClient;
PubSubClient client(espClient);

// Function to connect to WiFi
void connectWiFi() {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(500);
    }
    Serial.println("Connected to WiFi!");
    Serial.print("ESP IP Address: ");
    Serial.println(WiFi.localIP());
}

// Function to connect to MQTT Broker
void connectMQTT() {
    while (!client.connected()) {
        Serial.print("Connecting to MQTT...");
        if (client.connect("ESP8266_Client")) {
            Serial.println("Connected to MQTT!");
        } else {
            Serial.print("Failed, rc=");
            Serial.print(client.state());
            Serial.println(" Retrying in 5 seconds...");
            delay(5000);
        }
    }
}

void setup() {
    Serial.begin(9600);
    pinMode(SENSOR1, INPUT);
    pinMode(SENSOR2, INPUT);
    pinMode(LED, OUTPUT);

    connectWiFi();
    client.setServer(broker, 1883);  // Default MQTT port 1883
    connectMQTT();
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi Disconnected! Reconnecting...");
        connectWiFi();
    }
    
    if (!client.connected()) {
        Serial.println("MQTT Disconnected! Reconnecting...");
        connectMQTT();
    }
    client.loop();

    int sensor1_state = digitalRead(SENSOR1);
    int sensor2_state = digitalRead(SENSOR2);
    int analog_value = analogRead(ANALOG_SENSOR);

    // Store the analog value in the buffer
    analogSamples[sampleIndex] = analog_value;
    sampleIndex = (sampleIndex + 1) % SAMPLE_SIZE;
    if (sampleIndex == 0) bufferFilled = true;

    // Calculate average
    int total = 0;
    int sampleCount = bufferFilled ? SAMPLE_SIZE : sampleIndex;
    for (int i = 0; i < sampleCount; i++) {
        total += analogSamples[i];
    }
    float analog_avg = total / float(sampleCount);

    // Construct payload with node_id and values
    String payload = "{" + String(node_id) + " " + String(1) + " " + String(sensor1_state) + " " +
                           String(2) + " " + String(sensor2_state) + " " +
                           String(3) + " " + String(analog_value) + "}";

    Serial.print("Publishing: ");
    Serial.println(payload);
    Serial.print("Analog Value: ");
    Serial.print(analog_value);
    Serial.print(" | Average: ");
    Serial.println(analog_avg);

    client.publish(topic, payload.c_str());

    // LED ON if any digital sensor detects fire or analog exceeds dynamic threshold
    if (sensor1_state == HIGH || sensor2_state == HIGH || analog_value > analog_avg + 20) {
        digitalWrite(LED, HIGH);
    } else {
        digitalWrite(LED, LOW);
    }

    delay(1000);
}

