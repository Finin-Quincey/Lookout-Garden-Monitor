"""
GPIO Manager

This module is responsible for interacting with all the electronics connected to the GPIO pins.

Some day, there will be more text here...
"""

import pigpio as gpio # GPIO control library

### Constants ###

# N.B. This is the BCM pin numbering scheme
PIR_SENSOR_PIN   = 10
POWER_BUTTON_PIN = 3
POWER_LED_PIN    = 22
BUZZER_PIN       = 4
IR_LED_PIN_1     = 23
IR_LED_PIN_2     = 24

# Here we're using an audible frequency so we can, well, hear it! Note that the circuit is designed to resonate at 31kHz
# so it won't be as loud at other frequencies, and there may also be artefacts/aliasing disrupting the tone
BUZZER_FREQUENCY = 6000 # 6kHz is the minimum rated frequency for the buzzer

REFRESH_RATE = 20 # Number of times per second to update the gpio outputs

### Setup ###

log.info("Initialising GPIO pins")

pi = gpio.pi() # Init GPIO object

pi.set_mode(PIR_SENSOR_PIN,   gpio.INPUT)
pi.set_mode(POWER_BUTTON_PIN, gpio.INPUT)
pi.set_mode(POWER_LED_PIN,    gpio.OUTPUT)
pi.set_mode(BUZZER_PIN,       gpio.ALT0) # ALT0 is GPCLK for pin 4 (see https://pinout.xyz for a list of ALT functions for each pin)
pi.set_mode(IR_LED_PIN_1,     gpio.OUTPUT)
pi.set_mode(IR_LED_PIN_2,     gpio.OUTPUT)

pi.set_pull_up_down(POWER_BUTTON_PIN, gpio.PUD_UP)

### Functions ###

def get_pir_state():
    """  """
    return pi.read(PIR_SENSOR_PIN)