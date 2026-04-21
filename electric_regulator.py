from machine import Pin, ADC
import time

# --- CONFIGURATION ---
# Standard 240V Limits (UK/EU/AU Standards: 230V +10%/-6%)
MAX_VOLTAGE = 224  # Trip if above this
MIN_VOLTAGE = 216  # Trip if below this
SIMULATION_MAX = 300 # The pot's max position equals 300V

# --- HARDWARE SETUP ---
# ADC0 is typically GP26 on the Pico
voltage_sensor = ADC(26) 
# Relay connected to GP15
relay = Pin(15, Pin.OUT)
# Onboard LED for visual status
led = Pin(25, Pin.OUT)

def get_grid_voltage():
    # Read 16-bit value (0-65535)
    raw_value = voltage_sensor.read_u16()
    # Map 0-65535 to 0-300 Volts for simulation
    simulated_volts = (raw_value / 65535) * SIMULATION_MAX
    return round(simulated_volts, 1)

def safety_disconnect(reason):
    print(f"!!! DANGER: {reason} !!! - DISCONNECTING LOAD")
    relay.value(0) # Turn OFF Relay (Open Circuit)
    led.value(0)   # Turn OFF LED
    
def safe_reconnect():
    print("Grid Stable. Reconnecting...")
    relay.value(1) # Turn ON Relay (Closed Circuit)
    led.value(1)   # Turn ON LED

# --- MAIN LOOP ---
print("System Initialized. Monitoring Grid...")
relay.value(1) # Start connected (assuming safe start)

while True:
    grid_v = get_grid_voltage()
    print(f"Current Voltage: {grid_v}V")

    # Check for Unsafe Conditions
    if grid_v > MAX_VOLTAGE:
        safety_disconnect(f"Overvoltage ({grid_v}V)")
        time.sleep(2) # Force a wait before checking again
        
    elif grid_v < MIN_VOLTAGE:
        safety_disconnect(f"Undervoltage ({grid_v}V)")
        time.sleep(2)
        
    else:
        # Logic to reconnect ONLY if relay is currently off
        if relay.value() == 0:
            print("Voltage within safe range...")
            time.sleep(3) # Stabilization delay (Prevent chatter)
            # Re-check one last time before clicking on
            if MIN_VOLTAGE < get_grid_voltage() < MAX_VOLTAGE:
                safe_reconnect()
    
    time.sleep(0.5) # Update speed

