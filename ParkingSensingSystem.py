import time
from bluepy.btle import Peripheral, BTLEException, UUID
import RPi.GPIO as GPIO

# GPIO pin configuration for ultrasonic sensor
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24

# Set up GPIO mode and pin states
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ULTRASONIC_TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ULTRASONIC_ECHO_PIN, GPIO.IN)

def measure_distance_cm():
    """
    Measures the distance using the ultrasonic sensor and returns it in centimeters.
    """
    # Ensure the trigger pin is low
    GPIO.output(ULTRASONIC_TRIGGER_PIN, False)
    time.sleep(2)

    # Generate a short 10us pulse on the trigger pin
    GPIO.output(ULTRASONIC_TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(ULTRASONIC_TRIGGER_PIN, False)

    # Measure the duration of the echo pulse
    while GPIO.input(ULTRASONIC_ECHO_PIN) == 0:
        pulse_start_time = time.time()

    while GPIO.input(ULTRASONIC_ECHO_PIN) == 1:
        pulse_end_time = time.time()

    # Calculate the distance based on the pulse duration
    pulse_duration = pulse_end_time - pulse_start_time
    distance_cm = pulse_duration * 17150
    distance_cm = round(distance_cm, 2)

    return distance_cm

def attempt_bluetooth_connection(device_address):
    """
    Continuously attempts to connect to the specified Bluetooth device.
    """
    while True:
        try:
            print(f"Attempting to connect to Bluetooth device at {device_address}")
            ble_device = Peripheral(device_address, "public")
            return ble_device
        except BTLEException as e:
            print(f"Failed to connect: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def main():
    arduino_ble_address = "EC:62:60:81:68:DE"
    ble_device = attempt_bluetooth_connection(arduino_ble_address)

    battery_service_uuid = UUID("180A")
    battery_level_char_uuid = UUID("2A06")
    battery_service = ble_device.getServiceByUUID(battery_service_uuid)
    battery_level_char = battery_service.getCharacteristics(battery_level_char_uuid)[0]

    try:
        while True:
            try:
                # Measure the distance from the ultrasonic sensor
                distance_cm = measure_distance_cm()
                scaled_distance_value = int((distance_cm / 500.0) * 255)
                scaled_distance_value = max(0, min(255, scaled_distance_value))
                print(f"Measured distance: {distance_cm} cm, Scaled value: {scaled_distance_value}")

                # Write the scaled distance value to the Bluetooth characteristic
                battery_level_char.write(bytes([scaled_distance_value]), withResponse=True)
                print(f'Successfully sent scaled distance value: {scaled_distance_value}')
                time.sleep(1)
            except BTLEException as e:
                print(f'Error during communication: {e}')
                ble_device.disconnect()
                ble_device = attempt_bluetooth_connection(arduino_ble_address)
                battery_service = ble_device.getServiceByUUID(battery_service_uuid)
                battery_level_char = battery_service.getCharacteristics(battery_level_char_uuid)[0]
    except KeyboardInterrupt:
        # Cleanup GPIO settings and disconnect Bluetooth device on exit
        GPIO.cleanup()
        ble_device.disconnect()
        print("Clean exit: Disconnected from Bluetooth device and GPIO cleaned up")

if __name__ == "__main__":
    main()
