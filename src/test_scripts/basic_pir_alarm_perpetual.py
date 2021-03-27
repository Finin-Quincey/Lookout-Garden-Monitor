"""
Basic PIR Alarm (Perpetual Version)

A very simple script to demonstrate using the PIR sensor, buzzer and power button. Sounds a high-pitched tone and illuminates the
power button whenever the PIR sensor is active. Pressing the power button toggles whether the buzzer activates or not.

Author: Finin Quincey
"""

import time
import pigpio as gpio

### Constants ###

# N.B. This is the BCM pin numbering scheme
PIR_SENSOR_PIN   = 10
POWER_LED_PIN    = 22
POWER_BUTTON_PIN = 3
BUZZER_PIN       = 4
#IR_LED_PIN_1    = 23
#IR_LED_PIN_2    = 24

# Here we're using an audible frequency so we can, well, hear it! Note that the circuit is designed to resonate at 31kHz
# so it won't be as loud at other frequencies, and there may also be artefacts/aliasing disrupting the tone
BUZZER_FREQUENCY = 6000 # 6kHz is the minimum rated frequency for the buzzer

REFRESH_RATE = 20 # Number of times per second to update the gpio outputs

### Setup ###

pi = gpio.pi()

pi.set_mode(PIR_SENSOR_PIN,   gpio.INPUT)
pi.set_mode(POWER_LED_PIN,    gpio.OUTPUT)
pi.set_mode(POWER_BUTTON_PIN, gpio.INPUT)
pi.set_mode(BUZZER_PIN,       gpio.ALT0)
#pi.set_mode(IR_LED_PIN_1,     gpio.OUTPUT)
#pi.set_mode(IR_LED_PIN_2,     gpio.OUTPUT)

pi.set_pull_up_down(POWER_BUTTON_PIN, gpio.PUD_UP)

### Main Loop ###

# There are several possible approaches here:
# 1. Refresh the loop at regular intervals, check inputs and and update the outputs accordingly (as below)
# 2. Use pigpio's wait_for_edge function (although this effectively does the same thing, and we can't interrupt it unless we
#    terminate the program with a callback or something)
# 3. Use pigpio's callback functionality. This is not particularly useful here but may come in very handy when we're also
#    processing images at 1-2fps!

wasActive = False
standby = False
btnWasPressed = False

while True:

    active = not standby and pi.read(PIR_SENSOR_PIN) == 1

    if active != wasActive:
        pi.write(POWER_LED_PIN, 1 if active else 0)
        pi.hardware_clock(BUZZER_PIN, BUZZER_FREQUENCY if active else 0)
        wasActive = active
    
    if pi.read(POWER_BUTTON_PIN):
        if not btnWasPressed:
            btnWasPressed = True
            standby = not standby
    else:
        btnWasPressed = False

    time.sleep(1/REFRESH_RATE)