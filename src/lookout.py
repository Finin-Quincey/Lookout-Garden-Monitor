"""
Lookout

This is the main control script for the Lookout garden monitor, responsible for executing the overall program flow (as
defined in the UML activity diagram), coordinating and timing the vision and gpio, and auxiliary functions such as
shutting down the pi when the power button is pressed.
"""

DEBUG = True

import os                      # System commands
import time                    # Timing functions
from datetime import datetime  # Real-world date and time
import logging as log          # Log messages and log file output
from enum import Enum          # Enumeration types

# Must set up logger before importing our own modules or it won't work properly
log.basicConfig(format = "%(asctime)s [%(levelname)s] %(message)s",
                datefmt = "%d-%m-%Y %I:%M:%S %p",
                level = log.DEBUG if DEBUG else log.INFO,
                handlers = [
                    # Print to console and write to a log file
                    log.FileHandler(f"{os.getcwd()}/logs/{datetime.now().strftime('%Y-%m-%d_%H%M')}.log"),
                    log.StreamHandler()
                ])

log.info("*** Lookout started ***")

import gpio_manager as gpio

### Constants ###

BUZZ_TIME = 10 # Buzzer active time in seconds
IDLE_TIME = 30 # If no objects are detected in the camera feed for this many seconds, the 

# Objects in this list will trigger the buzzer if present, as long as no whitelisted objects are present
OBJECT_BLACKLIST = ["cat", "person"]
# Objects in this list will prevent the buzzer from triggering (disarm it) if present
OBJECT_WHITELIST = ["bat", "scissors"]

# N.B. Because we're using a callback approach here, we can't just have a shutdown method, we also need a way of
# preventing any callbacks from executing. The only way of doing this is to have the callback exit early when the state
# changes to shutting down. (Also, a state pattern would probably be overkill here)
class State(Enum):
    """Enum representing the different states the program can be in"""
    INACTIVE      = "Inactive"      # Waiting to be triggered via the PIR sensor
    ACTIVE        = "Active"        # Currently recording footage
    SHUTTING_DOWN = "Shutting down" # Waiting to shut down the pi (saving and exiting)

### Setup ###

# Global variables
state = State.INACTIVE

# Callbacks
log.info("Setting up callbacks")

# Testing stuff
gpio.get_pir_state()
gpio.set_power_led_state(True)
time.sleep(2)
gpio.set_power_led_state(False)