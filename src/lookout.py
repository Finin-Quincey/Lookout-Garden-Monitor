"""
Lookout

This is the main control script for the Lookout garden monitor, responsible for executing the overall program flow (as
defined in the UML activity diagram), coordinating and timing the vision and gpio, and auxiliary functions such as
shutting down the pi when the power button is pressed.

Author: Finin Quincey
"""

import os                      # Operating system commands
import sys                     # Python system commands
import time                    # Timing functions
from datetime import datetime  # Real-world date and time
import logging as log          # Log messages and log file output
from enum import Enum          # Enumeration types
import cv2                     # OpenCV for image processing
import threading               # Concurrency
import signal                  # System exit signals

### Constants ###

FORCE_SHUTDOWN_TIME = 5 # If the power button is held for longer than this many seconds, it forces a shutdown

# N.B. Because we're using a callback approach here, we can't just have a shutdown method, we also need a way of
# preventing any callbacks from executing. The only way of doing this is to have the callback exit early when the state
# changes to shutting down. (Also, a state pattern would probably be overkill here, this is Python not Java!)
class State(Enum):
    """Enum representing the different states the program can be in"""
    INACTIVE      = "Inactive"      # Waiting to be triggered via the PIR sensor
    ACTIVE        = "Active"        # Currently recording footage
    SHUTTING_DOWN = "Shutting down" # Waiting to shut down the pi (saving and exiting)
    
### Initial Setup ###

# Global variables
state = State.INACTIVE
idle_timer = 0
buzzer_timer = 0
btn_hold_timer = 0

# Initialise other modules
import settings
import gpio_manager as gpio
gpio.set_power_led_state(True)
gpio.enable_pir_sensor(True)
import camera_manager as camera
import object_detector

if settings.DEV_MODE:
    camera.display_current() # Show blank screen
    cv2.waitKey(2) # For some reason it needs 2ms

### Functions ###

def on_pir_activated():
    """
    Called from the GPIO manager when the PIR sensor activates.
    """
    log.info("PIR sensor activated")
    global state
    state = State.ACTIVE
    
def on_power_btn_pressed(released):
    """
    Called from the GPIO manager when the power button is pressed or released.
    """
    global btn_hold_timer
    
    if released:
        
        if btn_hold_timer != 0 and time.perf_counter() - btn_hold_timer > FORCE_SHUTDOWN_TIME:
            
            log.warning("Forcing shutdown! Capture data may be lost!")
            
            if settings.DEV_MODE:
                os.kill(os.getpid(), signal.SIGINT) # sys.exit() won't work here
            else:
                os.system("sudo shutdown -h now")
            
        else:
    
            log.info("Shutting down...")
            
            global state
            state = State.SHUTTING_DOWN
            
            gpio.set_power_led_state(True)
        
    else:
        btn_hold_timer = time.perf_counter() # Start hold timer

def capture_video():
    """
    Captures a video from the camera until no objects are present any more (or until the buffer is full), performing object
    detection and controlling the buzzer accordingly.
    
    Returns:
    - True if the device should go back to sleep, False if it should shut down
    """
    
    global idle_timer
    global buzzer_timer

    i = 0
    measured_framerate = 0
    
    while True: # Capture until one of the return statements below is reached
        
        t = time.perf_counter()
        
        camera.capture_frame()
        
        boxes = object_detector.boxes
        labels = object_detector.labels
        scores = object_detector.scores
        
        if len(labels) > 0: # If we found something
    
            idle_timer = time.perf_counter() # Reset idle timer
            
            # Check objects against blacklist/whitelist
            if settings.ENABLE_BUZZER and any(item in settings.OBJECT_BLACKLIST for item in labels) and all(item1 not in settings.OBJECT_WHITELIST for item1 in labels):
                # Activate the buzzer and start the timer
                if buzzer_timer == 0: gpio.set_buzzer_frequency(settings.BUZZER_FREQUENCY)
                buzzer_timer = time.perf_counter()
                
        if buzzer_timer != 0 and time.perf_counter() - buzzer_timer >= settings.BUZZ_TIME: # If buzzer time has elapsed
            # Deactivate the buzzer and reset the timer
            gpio.set_buzzer_frequency(0)
            buzzer_timer = 0
        
        camera.annotate_current(boxes, labels, scores, measured_framerate, buzzer_timer != 0)
        
        if settings.DEV_MODE:
            camera.display_current()
        
        if not camera.store_current(): # Stop recording if the buffer is full
            log.info("Buffer full, stopping current recording")
            return True
            
        if time.perf_counter() - idle_timer >= settings.IDLE_TIME: # If idle time has elapsed
            return True
        
        if state == State.SHUTTING_DOWN:
            return False
        
        # LED flashing
        if i == 20:
            gpio.set_power_led_state(True)
            i = 0
        else:
            if i == 0:
                gpio.set_power_led_state(False)
            i += 1
        
        measured_framerate = min(settings.FRAMERATE, round(1/(time.perf_counter() - t), 1))
        
        # Try to keep a stable framerate by waiting for the rest of the time, if any
        cv2.waitKey(max(1, int(1000 * (1.0/settings.FRAMERATE - (time.perf_counter() - t)))))

### Finish Setup ###

log.info("Setting up callbacks")

gpio.init_pir_callback(on_pir_activated)
gpio.init_btn_callback(on_power_btn_pressed)

gpio.set_power_led_state(False)

log.info("Setup done")

### Main Logic Loop ###

while state != State.SHUTTING_DOWN: # Keep doing this until the program shuts down
    
    if state == State.ACTIVE:
        
        idle_timer = time.perf_counter() # Start idle timer
        
        gpio.set_ir_led_state(True)
        camera.open(settings.SAVE_DIRECTORY) # Do this as close to first capture as possible to minimise delay
    
        if capture_video():
            # capture_video() returned True so go back to sleep
            log.debug("Going back to sleep, goodnight")
            state = state.INACTIVE
            camera.close()
            gpio.set_buzzer_frequency(0)
            gpio.set_ir_led_state(False)
        
    time.sleep(0.2) # Save processing power when not doing anything

### Shutdown ###

# Shut down modules and wait for other processes to finish
gpio.prepare_shutdown() # Cancel callbacks first
object_detector.shutdown() # Start shutdown of object detector
camera.shutdown() # Wait for camera to shut down
object_detector.thread.join() # Wait until object detector has finished (it probably has already, but just in case)

# Finally, turn off the power LED and close the GPIO connection once everything is done
gpio.finish_shutdown()

log.info("*** Exiting program ***")
    
if settings.DEV_MODE:
    sys.exit()
else:
    os.system("poweroff")