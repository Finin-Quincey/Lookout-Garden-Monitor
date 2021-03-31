"""
GPIO Manager

This module is responsible for interacting with all the electronics connected to the GPIO pins.

Author: Finin Quincey
"""

import logging as log
import pigpio as gpio # GPIO control library

### Constants ###

# N.B. This is the BCM pin numbering scheme
PIR_SENSOR_PIN   = 10
PIR_ENABLE_PIN   = 9
POWER_BUTTON_PIN = 3
POWER_LED_PIN    = 22
BUZZER_PIN       = 4
IR_LED_PIN_1     = 23
IR_LED_PIN_2     = 24

REFRESH_RATE = 20 # Number of times per second to update the gpio outputs

### Setup ###

# Initialise module variables
pir_callback = None
btn_callback = None
# Functions to call when forwarding callbacks to the main control script
pir_cb_forward = None
btn_cb_forward = None

# Init GPIO pins into the correct modes and pull up/downs

log.info("Initialising GPIO pins")

pi = gpio.pi() # Init GPIO object

pi.set_mode(PIR_SENSOR_PIN,   gpio.INPUT)
pi.set_mode(PIR_ENABLE_PIN,   gpio.OUTPUT)
pi.set_mode(POWER_BUTTON_PIN, gpio.INPUT)
pi.set_mode(POWER_LED_PIN,    gpio.OUTPUT)
pi.set_mode(BUZZER_PIN,       gpio.ALT0) # ALT0 is GPCLK for pin 4 (see https://pinout.xyz for a list of ALT functions for each pin)
pi.set_mode(IR_LED_PIN_1,     gpio.OUTPUT)
pi.set_mode(IR_LED_PIN_2,     gpio.OUTPUT)

pi.set_pull_up_down(POWER_BUTTON_PIN, gpio.PUD_UP) # Power button is active low

### Functions ###

def get_pir_state():
    """
    Returns the state of the PIR sensor pin. A value of 1 means the PIR is active; a value of 0 means it is inactive or
    disabled.
    """
    result = pi.read(PIR_SENSOR_PIN)
    log.debug("Read PIR pin (GPIO %i), level is %s", PIR_SENSOR_PIN, "HIGH" if result else "LOW")
    return result

def enable_pir_sensor(enable):
    """
    Enables or disables the PIR sensor.
    
    Parameters:
    - enable: True to enable the PIR sensor, False to disable it.
    """
    log.debug("Setting PIR enable pin (GPIO %i) to output %s", PIR_ENABLE_PIN, "HIGH" if enable else "LOW")
    pi.write(PIR_ENABLE_PIN, enable)

def set_power_led_state(state):
    """
    Sets the state of the power button LED.
    
    Parameters:
    - state: True to turn the LED on, False to turn it off.
    """
    log.debug("Setting LED pin (GPIO %i) to output %s", POWER_LED_PIN, "HIGH" if state else "LOW")
    pi.write(POWER_LED_PIN, state)
    
def set_ir_led_state(state):
    """
    Sets the state of the infrared LED lamps. Note that when turned on, the lamps control their own brightness based on
    the inbuilt photoresistors; this function simply controls whether they receive power or not.
    
    Parameters:
    - state: True to turn the IR LEDs on, False to turn them off.
    """
    log.debug("Setting IR LED pins (GPIO %i & %i) to output %s", IR_LED_PIN_1, IR_LED_PIN_2, "HIGH" if state else "LOW")
    pi.write(IR_LED_PIN_1, state)
    pi.write(IR_LED_PIN_2, state)
    
def set_buzzer_frequency(frequency):
    """
    Sets the buzzer to the given frequency. Set to 0 to turn the buzzer off.
    """
    pi.hardware_clock(BUZZER_PIN, frequency)
    
def prepare_shutdown():
    """
    Resets all output pins to their 'off' states (except the power LED), cleans up callbacks, and so on.
    """
    # Chances are none of this is necessary as we're shutting the pi down anyway, but there's no harm in doing it anyway
    
    log.info("Shutting down GPIO")
    
    global pir_callback
    global btn_callback
    global pi
    
    # For now we need to turn this off for shutdown or it will stay on, at some point I may look into ways of turning it
    # off later on in the shutdown sequence but it doesn't really matter that much - the main thing is that it stays on
    # while the video is saving
    enable_pir_sensor(False)
    set_ir_led_state(False)
    set_buzzer_frequency(0)
    
    pir_callback.cancel()
    btn_callback.cancel()
    
def finish_shutdown():
    """
    Turns off the power LED and closes the GPIO connection.
    """
    set_power_led_state(False)
    pi.stop()
    
### Callbacks ###
    
# So as not to create circular dependencies, the callback functions (which need to trigger stuff in the main lookout.py
# module) are passed into here from that module on startup. It's not good practice to call functions in higher-level code
# from lower-level code, especially when you're already doing it the other way round - sure, it doesn't really matter here
# but the programmer in me is insisting that I do this properly!

def init_pir_callback(func):
    """
    Registers the given function to be called when the PIR sensor activates, and sets up the GPIO interrupt.
    """
    global pir_callback
    global pir_cb_forward
    global pi
    pir_cb_forward = func
    pir_callback = pi.callback(PIR_SENSOR_PIN, gpio.RISING_EDGE, pir_pin_callback)
    
def init_btn_callback(func):
    """
    Registers the given function to be called when the power button is pressed, and sets up the GPIO interrupt.
    """
    global btn_callback
    global btn_cb_forward
    global pi
    btn_cb_forward = func
    # Using either edge so we can keep track of how long the button was pressed for
    btn_callback = pi.callback(POWER_BUTTON_PIN, gpio.EITHER_EDGE, btn_pin_callback)

def pir_pin_callback(pin, level, tick):
    log.debug("PIR sensor callback triggered (GPIO %i)", pin)
    if level != 1:
        log.warn("Unexpected callback value on GPIO %i: %i (probably a timeout)", pin, level)
        return # Sanity check: ignore if it wasn't a rising edge (only happens on timeout)
    pir_cb_forward() # Pass control flow up to the main lookout class
    
def btn_pin_callback(pin, level, tick):
    log.debug("Power button callback triggered (GPIO %i)", pin)
    if level > 1:
        log.warn("Unexpected callback value on GPIO %i: %i (probably a timeout)", pin, level)
        return # Sanity check: ignore if it wasn't a rising edge (only happens on timeout)
    btn_cb_forward(level == 1) # Pass control flow up to the main lookout class