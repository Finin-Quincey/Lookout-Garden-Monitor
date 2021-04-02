"""
Settings

This module is responsible for reading and storing the program settings.
"""

import logging as log
import json  # JSON file parsing
import os
from datetime import datetime  # Real-world date and time

### Constants ###

# Development mode is used when the pi is plugged into a monitor, mouse and keyboard, and has the following effects:
# - The annotated camera feed is displayed on-screen
# - Logging is set to DEBUG level instead of INFO so that DEBUG messages are logged as well
# - When the power button is pressed, the program exits rather than shutting down the pi
# - The directory used to save and load files is set to the Python working directory instead of the USB drive
DEV_MODE = False

SAVE_DIRECTORY = os.getcwd() if DEV_MODE else "/media/pi/1234-5678/Lookout"

# Default Values

ENABLE_BUZZER = True

# For development purposes we're using an audible frequency so we can, well, hear it! Note that the circuit is designed to
# resonate at 31kHz so it won't be as loud at other frequencies, and there may be artefacts/aliasing disrupting the tone
BUZZER_FREQUENCY = 6000 if DEV_MODE else 31000 # 6kHz is the minimum rated frequency for the buzzer

BUZZ_TIME = 10 # Buzzer active time in seconds
IDLE_TIME = 20 # If no objects are detected in the camera feed for this many seconds, the device returns to inactive state

# Objects in this list will trigger the buzzer if present, as long as no whitelisted objects are present
OBJECT_BLACKLIST = ["cat", "person", "dog"]
# Objects in this list will prevent the buzzer from triggering (disarm it) if present
OBJECT_WHITELIST = ["scissors"]

FRAME_BUFFER_SIZE = 150 # Maximum number of frames the buffer can hold; prevents overloading the RAM
FRAMERATE = 10          # Target framerate to capture at, in frames per second

MODEL_NAME = f"{SAVE_DIRECTORY}/models/Sample_TFLite_model"  # Path to the model directory

CONFIDENCE_THRESHOLD = 0.6 # Minimum confidence for an object to count as a detection

# All objects not in this list will be filtered out
VALID_OBJECTS = ["person", "cat", "dog", "bird", "horse", "sheep", "cow", "scissors"]

### Setup ###

# Must set up logger before importing our own modules or it won't work properly
log.basicConfig(format = "%(asctime)s [%(levelname)s] %(message)s",
                datefmt = "%d-%m-%Y %I:%M:%S %p",
                level = log.DEBUG if DEV_MODE else log.INFO,
                handlers = [
                    # Print to console and write to a log file
                    log.FileHandler(f"{SAVE_DIRECTORY}/logs/{datetime.now().strftime('%Y-%m-%d_%H%M')}.log"),
                    log.StreamHandler()
                ])

log.info("*** Lookout started ***")

# Read config file
try:
    with open(f"{SAVE_DIRECTORY}/config.json") as reader:
        log.info("Reading config settings")
        settings = json.load(reader)
        
    ENABLE_BUZZER    = settings["enable_buzzer"]
    BUZZER_FREQUENCY = settings["buzzer_frequency"]
    BUZZ_TIME        = settings["buzz_time"]
    IDLE_TIME        = settings["idle_time"]
    OBJECT_BLACKLIST = settings["object_blacklist"]
    OBJECT_WHITELIST = settings["object_whitelist"]
    
    FRAME_BUFFER_SIZE    = settings["frame_buffer_size"]
    FRAMERATE            = settings["framerate"]
    CONFIDENCE_THRESHOLD = settings["confidence_threshold"]
    VALID_OBJECTS        = settings["valid_objects"]

    MODEL_NAME = f"{SAVE_DIRECTORY}/models/{settings['model_name']}"
    
# Handle errors
except json.JSONDecodeError:
    log.error("Error opening config.json, using default setting values instead")
except KeyError:
    log.error("config.json is missing one or more keys, using default setting values instead")