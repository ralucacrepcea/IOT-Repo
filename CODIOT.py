import RPi.GPIO as GPIO     # Import the RPi.GPIO module for controlling the GPIO pins on the Raspberry Pi
import time                 # Import the time module for adding delays
import pyrebase             # Import the pyrebase module for interacting with Firebase

# Firebase configuration details
config = {
    "apiKey": "AIzaSyCktGAXz8bYFaUGN6lUGkLUcWfXFMtHt-w",
    "authDomain": "detector-fb6c7.firebaseapp.com",
    "databaseURL": "https://detector-fb6c7-default-rtdb.firebaseio.com/",
    "storageBucket": "detector-fb6c7.appspot.com"
}

firebase = pyrebase.initialize_app(config)  # Initialize the Firebase app with the given configuration
db = firebase.database()                    # Get a reference to the Firebase real-time database

GPIO.setmode(GPIO.BOARD)     # Set the GPIO mode to BOARD to use physical pin numbers
GPIO.setwarnings(False)      # Disable warnings

# Define the pin numbers for the various components
red_pin = 11
green_pin = 13
smoke_pin = 21
buzzer_pin = 15
relay_pin = 23  # Pin for the relay controlling the water pump

GPIO.setup(red_pin, GPIO.OUT)      # Set up the red LED pin as an output
GPIO.setup(green_pin, GPIO.OUT)    # Set up the green LED pin as an output
GPIO.setup(smoke_pin, GPIO.IN)     # Set up the smoke sensor pin as an input
GPIO.setup(buzzer_pin, GPIO.OUT)   # Set up the buzzer pin as an output
GPIO.setup(relay_pin, GPIO.OUT)    # Set up the relay pin as an output

GPIO.output(red_pin, GPIO.LOW)     # Turn off the red LED initially
GPIO.output(green_pin, GPIO.HIGH)  # Turn on the green LED initially
GPIO.output(buzzer_pin, GPIO.LOW)  # Turn off the buzzer initially
GPIO.output(relay_pin, GPIO.HIGH)  # Ensure relay is initially off

# Function to generate sound with the buzzer
def generate_sound():
    for _ in range(500):                   # Loop 500 times
        GPIO.output(buzzer_pin, GPIO.HIGH) # Turn on the buzzer
        time.sleep(0.001)                  # Wait for 1 millisecond
        GPIO.output(buzzer_pin, GPIO.LOW)  # Turn off the buzzer
        time.sleep(0.001)                  # Wait for 1 millisecond

# Function to activate the relay (water pump)
def activate_relay():
    GPIO.output(relay_pin, GPIO.HIGH)      # Turn on the relay (water pump)
    print("Water pump activated")          # Print message for debugging
    data = {"status": "Pump activated"}    # Create a data dictionary with the status
    db.child("Pump_status").push(data)     # Push the data to Firebase under "Pump_status"
    time.sleep(5)                          # Keep relay on for 5 seconds
    GPIO.output(relay_pin, GPIO.LOW)       # Turn off relay after 5 seconds
    print("Water pump activated")          # Print message for debugging (repeated message)
    data = {"status": "Pump dezactivated"} # Create a data dictionary with the status
    db.child("Pump_status").push(data)     # Push the data to Firebase under "Pump_status"

# Callback function for handling smoke detection
def callback(channel):
    if GPIO.input(smoke_pin):               # If smoke is detected
        print("Smoke detected")             # Print message for debugging
        GPIO.output(red_pin, GPIO.HIGH)     # Turn on the red LED
        GPIO.output(green_pin, GPIO.LOW)    # Turn off the green LED
        generate_sound()                    # Generate sound with the buzzer
        data = {"status": "Smoke detected"} # Create a data dictionary with the status
        db.child("Smoke_status").push(data) # Push the data to Firebase under "Smoke_status"
        activate_relay()                    # Activate water pump when fire is detected
    else:
        print("Smoke not detected")             # If smoke is not detected, print message for debugging
        GPIO.output(red_pin, GPIO.LOW)          # Turn off the red LED
        GPIO.output(green_pin, GPIO.HIGH)       # Turn on the green LED
        data = {"status": "No smoke detected"}  # Create a data dictionary with the status
        db.child("smoke_status").push(data)     # Push the data to Firebase under "smoke_status"

# Add event detection on the smoke sensor pin for both rising and falling edges, with a debounce time of 300ms
GPIO.add_event_detect(smoke_pin, GPIO.BOTH, bouncetime=300)
# Add a callback function to be called when an event is detected on the smoke sensor pin
GPIO.add_event_callback(smoke_pin, callback)

try:
    while True:       # Infinite loop to keep the script running
        time.sleep(1) # Wait for 1 second

except KeyboardInterrupt: # Catch a keyboard interrupt (Ctrl+C)
    GPIO.cleanup()        # Clean up the GPIO pins
