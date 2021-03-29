"""
Lookout

This is the main control script for the Lookout garden monitor, responsible for executing the overall program flow (as
defined in the UML activity diagram), coordinating and timing the vision and gpio, and auxiliary functions such as
shutting down the pi when the power button is pressed.

Author: Finin Quincey
"""

# Development mode is used when the pi is plugged into a monitor, mouse and keyboard, and has the following effects:
# - The annotated camera feed is displayed on-screen
# - Logging is set to DEBUG level instead of INFO so that DEBUG messages are logged as well
# - When the power button is pressed, the program exits rather than shutting down the pi
DEV_MODE = True

import os                      # Operating system commands
import sys                     # Python system commands
import time                    # Timing functions
from datetime import datetime  # Real-world date and time
import logging as log          # Log messages and log file output
from enum import Enum          # Enumeration types
import cv2
import threading

# Must set up logger before importing our own modules or it won't work properly
log.basicConfig(format = "%(asctime)s [%(levelname)s] %(message)s",
                datefmt = "%d-%m-%Y %I:%M:%S %p",
                level = log.DEBUG if DEV_MODE else log.INFO,
                handlers = [
                    # Print to console and write to a log file
                    log.FileHandler(f"{os.getcwd()}/logs/{datetime.now().strftime('%Y-%m-%d_%H%M')}.log"),
                    log.StreamHandler()
                ])

### Constants ###

BUZZ_TIME = 10 # Buzzer active time in seconds
IDLE_TIME = 30 # If no objects are detected in the camera feed for this many seconds, the device returns to inactive state
FRAMERATE = 20 # Target framerate to capture at, in frames per second

# Objects in this list will trigger the buzzer if present, as long as no whitelisted objects are present
OBJECT_BLACKLIST = ["cat", "person"]
# Objects in this list will prevent the buzzer from triggering (disarm it) if present
OBJECT_WHITELIST = ["bat", "scissors"]

# N.B. Because we're using a callback approach here, we can't just have a shutdown method, we also need a way of
# preventing any callbacks from executing. The only way of doing this is to have the callback exit early when the state
# changes to shutting down. (Also, a state pattern would probably be overkill here, this is Python not Java!)
class State(Enum):
    """Enum representing the different states the program can be in"""
    INACTIVE      = "Inactive"      # Waiting to be triggered via the PIR sensor
    ACTIVE        = "Active"        # Currently recording footage
    SHUTTING_DOWN = "Shutting down" # Waiting to shut down the pi (saving and exiting)
    
### Initial Setup ###

log.info("*** Lookout started ***")

# Global variables
state = State.INACTIVE

import gpio_manager as gpio
gpio.set_power_led_state(True)

import camera_manager as camera
import object_detector

### Callbacks ###

def on_pir_activated():
    """
    Called from the GPIO manager when the PIR sensor activates.
    """
    log.debug("PIR sensor activated")
    
    global state
    state = State.ACTIVE
    
    # TODO: Most of the high-level logic goes here
    
def on_power_btn_pressed():
    """
    Called from the GPIO manager when the power button is pressed.
    """
    log.info("Shutting down...")
    
    global state
    global callback_thread
    state = State.SHUTTING_DOWN
    callback_thread = threading.current_thread()
    
    gpio.set_power_led_state(True)
    
    camera.shutdown()
    object_detector.shutdown()
    gpio.shutdown()
    
    if DEV_MODE:
        sys.exit()
    else:
        os.system("sudo shutdown -h now")

### Finish Setup ###

log.info("Setting up callbacks")

gpio.init_pir_callback(on_pir_activated)
gpio.init_btn_callback(on_power_btn_pressed)

gpio.set_power_led_state(False)

log.info("Setup done")

i = 0

camera.open() # This has to be done right before capturing starts or there will be a delay

# LED flashing
while state != State.SHUTTING_DOWN:
    
    t = time.perf_counter()
    
    camera.capture_frame()
    
    boxes = object_detector.boxes
    labels = object_detector.labels
    scores = object_detector.scores
    
    # Object whitelist/blacklist logic goes here
    
    camera.annotate_current(boxes, labels, scores)
    
    if DEV_MODE:
        camera.display_current()
    
    if i == 20:
        gpio.set_power_led_state(True)
        i = 0
    else:
        if i == 0:
            gpio.set_power_led_state(False)
        i += 1
    
    # Try to keep a stable framerate by waiting for the rest of the time, if any
    cv2.waitKey(max(1, int(1000 * (1.0/FRAMERATE - (time.perf_counter() - t)))))
    
# Wait until callbacks and object detection have finished
# This prevents the main thread (and hence the program) from terminating until all other threads are done
callback_thread.join()
object_detector.thread.join()

log.info("*** Exiting program ***")