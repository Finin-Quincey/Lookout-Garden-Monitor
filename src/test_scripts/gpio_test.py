"""
GPIO Test

Very basic test of the GPIO pins, to verify that the circuitry is working as intended. Tests each part of the circuit in turn:
1. Emits a 6kHz tone from the buzzer for 3 seconds
2. Blinks the power LED 3 times
3. Prints out the current state of the PIR sensor
"""

import time
import os
import pigpio as gpio

# Despite the common assertion that Python is the easiest way to program on a Pi, when it comes to GPIO libraries the choice is a bit confusing!
# (Ironically, in Java there's only Pi4J and it uses WiringPi numbers so everything is nice and simple...)
# There are several libraries to choose from:
# - gpiozero, a beginner's library designed to simplify things as much as possible. It is buit on top of the other libraries, and you can select which
#   it uses. It also allows you to translate between pin numbering schemes (including pyhsical) if you want, but it's BCM by default. Unsure if you can
#   use stuff like hardware clock with it.
# - WiringPI Python, a port of WiringPi (which is in C natively) that naturally uses its numbering scheme. It is incomplete in functionality though.
# - pigpio, the most up-to-date and comprehensive library as far as I can tell. Supports hardware clock and other more advanced functionality. Uses BCM
#   numbering. Can do remote GPIO as well.
# - RPi.GPIO, previously very popular but now outdated. Since uopdated and expanded on by RPIO, which is also not updated any more!

#os.system('sudo pigpiod');

# Interacting with the WiringPi gpio utility using shell commands
# N.B. this uses WiringPi's pin numbering scheme rather than the BCM numbers
#os.system('gpio mode 7 clock');
#os.system('gpio clock 7 6000');

# Using pigpio
pi = gpio.pi()
pi.set_mode(4, gpio.ALT0)
pi.hardware_clock(4, 6000)

time.sleep(3)

#os.system('gpio mode 7 in');
pi.hardware_clock(4, 0)

time.sleep(1)

pi.set_mode(22, gpio.OUTPUT)

for i in range(6):
    pi.write(22, i%2)
    time.sleep(1)

pi.set_mode(10, gpio.INPUT)

if pi.read(10):
    print("PIR sensor is active")
else:
    print("PIR sensor is inactive")