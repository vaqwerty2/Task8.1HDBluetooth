#include <ArduinoBLE.h>

const int ledPin = 9;
BLEService parkingService("180A"); // Defining the BLE Service
BLEUnsignedCharCharacteristic distanceChar("2A06", BLERead | BLENotify | BLEWrite); // Defining the BLE Characteristic

void setup() {
  Serial.begin(9600);
  while (!Serial);

  pinMode(ledPin, OUTPUT);

  if (!BLE.begin()) {
    Serial.println("Failed to initialize BLE!");
    while (1);
  }

  BLE.setLocalName("CarActuator");
  BLE.setAdvertisedService(parkingService);
  parkingService.addCharacteristic(distanceChar);
  BLE.addService(parkingService);

  distanceChar.writeValue(0);
  BLE.advertise();

  Serial.println("BLE device is now broadcasting...");
}

void loop() {
  BLEDevice centralDevice = BLE.central();

  if (centralDevice) {
    Serial.print("Connected to: ");
    Serial.println(centralDevice.address());

    while (centralDevice.connected()) {
      if (distanceChar.written()) {
        int receivedValue = distanceChar.value(); // This is the scaled distance
        Serial.print("Received scaled distance: ");
        Serial.println(receivedValue);

        // Map the scaled distance back to the original distance range (0 to 500 cm)
        int actualDistance = map(receivedValue, 0, 255, 0, 500);
        Serial.print("Approximated distance: ");
        Serial.println(actualDistance);
        
        // Set LED intensity based on the actual distance
        if (actualDistance < 5) {
          analogWrite(ledPin, 255); // 100% intensity
          Serial.println("LED at 100% intensity");
        } 
        else if (actualDistance < 10) {
          analogWrite(ledPin, 191); // 75% intensity
          Serial.println("LED at 75% intensity");
        } 
        else if (actualDistance < 15) {
          analogWrite(ledPin, 128); // 50% intensity
          Serial.println("LED at 50% intensity");
        } 
        else if (actualDistance < 20) {
          analogWrite(ledPin, 64); // 25% intensity
          Serial.println("LED at 25% intensity");
        } 
        else if (actualDistance > 30) {
          analogWrite(ledPin, 0); // LED OFF
          Serial.println("LED OFF");
        }
      }
      delay(1000);
    }
    Serial.print("Disconnected from: ");
    Serial.println(centralDevice.address());
  } 
  else {
    Serial.println("Attempting to reconnect...");
    BLE.advertise(); // Restart advertising
    delay(5000); // Wait for 5 seconds before retrying
  }
}
