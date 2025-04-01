#define SENSOR1 5    // GPIO5 (D1) - Digital Sensor 1
#define SENSOR2 4    // GPIO4 (D2) - Digital Sensor 2
#define ANALOG_SENSOR A0  // A0 - Analog Sensor
#define LED 0        // GPIO0 (D3) - LED

void setup() {
    pinMode(SENSOR1, INPUT);
    pinMode(SENSOR2, INPUT);
    pinMode(LED, OUTPUT);
    
    Serial.begin(9600); // Initialize Serial Monitor
    Serial.println("🔥 Sensor Monitoring System Initialized! 🔥");
    Serial.println("-------------------------------------------------");
}

void loop() {
    int sensor1_state = digitalRead(SENSOR1);
    int sensor2_state = digitalRead(SENSOR2);
    int analog_value = analogRead(ANALOG_SENSOR); // Read analog sensor value

    // Print the current state of all sensors
    Serial.print("[PORT 5] Sensor 1 State: ");
    Serial.print(sensor1_state);
    Serial.print(" | [PORT 4] Sensor 2 State: ");
    Serial.print(sensor2_state);
    Serial.print(" | [PORT A0] Analog Sensor Value: ");
    Serial.println(analog_value);

    // Fire detection logic
    if (sensor1_state == HIGH) {
        digitalWrite(LED, HIGH);
        Serial.println("🔥 Fire detected on Digital Sensor 1 (Port 5)!");
    }
    
    if (sensor2_state == HIGH) {
        digitalWrite(LED, HIGH);
        Serial.println("🔥 Fire detected on Digital Sensor 2 (Port 4)!");
    }

    // Example: Assume fire is detected if analog value crosses a threshold (e.g., 500)
    if (analog_value > 1200) {
        digitalWrite(LED, HIGH);
        Serial.println("🔥 Fire detected on Analog Sensor (Port A0)!");
    }

    // If no fire detected, turn off LED
    if (sensor1_state == LOW && sensor2_state == LOW && analog_value <= 1200) {
        digitalWrite(LED, LOW);
    }

    delay(2000); // Small delay for stability
}
