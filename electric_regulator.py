# Sparksync - Voltage Safety Simulation
# Team GridMinds

#USER INSTRUCTION
# This simulation uses a potentiometer to represent voltage input.
# Turn the potentiometer knob in the simulation to increase or decrease voltage. This mimics real-world power flunctuations.
# The system will automatically detect if the voltage is safe (216V-224V)

from machine import Pin, ADC
import time

# --- CONFIGURATION ---
MAX_VOLTAGE = 224
MIN_VOLTAGE = 216
SIMULATION_MAX = 300

# --- HARDWARE SETUP ---
voltage_sensor = ADC(26)

relay = Pin(15, Pin.OUT)

# ONBOARD LED (optional)
led = Pin(25, Pin.OUT)

# EXTERNAL LEDs (THIS WAS MISSING BEFORE)
green = Pin(8, Pin.OUT)
red = Pin(9, Pin.OUT)

def get_grid_voltage():
    raw_value = voltage_sensor.read_u16()
    simulated_volts = (raw_value / 65535) * SIMULATION_MAX
    return round(simulated_volts, 1)

def safety_disconnect(reason):
    print(f"!!! DANGER: {reason} !!! - DISCONNECT YOUR DEVICE")
    relay.value(0)
    led.value(0)

def safe_reconnect():
    print("Grid Stable. Reconnecting...")
    relay.value(1)
    led.value(1)

# --- MAIN LOOP ---
print("System Initialized. Monitoring Grid...")
relay.value(1)

while True:
    grid_v = get_grid_voltage()
    print(f"Current Voltage: {grid_v}V")

    # OVERVOLTAGE
    if grid_v > MAX_VOLTAGE:
        safety_disconnect(f"Overvoltage ({grid_v}V)")
        green.value(0)
        red.value(1)

    # UNDERVOLTAGE
    elif grid_v < MIN_VOLTAGE:
        safety_disconnect(f"Undervoltage ({grid_v}V)")
        green.value(0)
        red.value(1)

    # SAFE RANGE
    else:
        if relay.value() == 0:
            print("Voltage within safe range...")
            time.sleep(3)

            if MIN_VOLTAGE < get_grid_voltage() < MAX_VOLTAGE:
                safe_reconnect()

                # GREEN = SAFE
                green.value(1)
                red.value(0)

        else:
            # KEEP SAFE STATE VISUAL
            green.value(1)
            red.value(0)

    time.sleep(0.5)
