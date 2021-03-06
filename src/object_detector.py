"""
Object Detector

This module is responsible for interfacing with TensorFlow to perform object detection. All processing in this module is
handled in a separate thread so it does not significantly affect other operations; this means the video capture can happen
continuously while the object detection just reads the latest frame whenever it starts a new detection cycle (usually about
2 times per second).

Author: Finin Quincey

Based on the example script TFLite_detection_webcam.py by Evan Juras:
https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/TFLite_detection_webcam.py
"""

import logging as log
import os                     # Operating system commands
import time                   # Timing functions
import cv2                    # OpenCV functions
import numpy as np            # Matrix operations
from threading import Thread  # Concurrency
import importlib.util         # Library for importing TensorFlow stuff

import camera_manager as camera
import settings

### Constants ###

GRAPH_NAME           = "detect.tflite"  # Name of the graph (.tflite) file in the above directory
LABELMAP_NAME        = "labelmap.txt"   # Name of the label map (.txt) file in the above directory

# Derived values
PATH_TO_CKPT   = os.path.join(settings.MODEL_NAME, GRAPH_NAME)     # Path to .tflite file
PATH_TO_LABELS = os.path.join(settings.MODEL_NAME, LABELMAP_NAME)  # Path to label map file

### Setup ###

# Initialise module variables
boxes = []
labels = []
scores = []

shutdown_flag = False

log.info("Initialising TensorFlow model")

# Most of this is taken from the example scripts, minus the edge TPU stuff since we're not using that

# Import TensorFlow libraries
# If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
# If using Coral Edge TPU, import the load_delegate library
pkg = importlib.util.find_spec("tflite_runtime")
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    label_map = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if label_map[0] == '???':
    del(label_map[0])

# Load the Tensorflow Lite model.
interpreter = Interpreter(model_path=PATH_TO_CKPT)
interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Define target method for object detection thread
def run():
    
    log.info("Object detection thread started")
    
    time.sleep(1)
    
    while not shutdown_flag:
        if(camera.is_capturing()):
            process_next()
        else:
            time.sleep(0.2) # Save processing power when not capturing
        
    log.info("Object detection thread stopping")

# Create and start the object detection thread
thread = Thread(target = run, args = (), name = "Object-detection-thread")
thread.start()

### Functions ###

def shutdown():
    """
    Marks the object detector to shut down after the current cycle is finished
    """
    log.info("Marking object detector for shutdown")
    global shutdown_flag
    shutdown_flag = True

def process_next():
    """
    Performs object detection on the latest frame from the camera feed and updates the global variables with the results.
    """
    # Get latest frame from camera stream
    frame = camera.raw_frame.copy()

    # Resize to expected shape [1xHxWx3]
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    global boxes
    global labels
    global label_map
    global scores
    
    # Retrieve detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
    labels = np.array(label_map)[classes.astype(int)] # Convert classes to labels
    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects

    # Remove results that are below the confidence threshold
    idx = scores > settings.CONFIDENCE_THRESHOLD
    boxes = boxes[idx]
    labels = labels[idx]
    scores = scores[idx]
    
    # Remove results that are not in the list of valid objects
    idx = [label in settings.VALID_OBJECTS for label in labels]
    boxes = boxes[idx]
    labels = labels[idx]
    scores = scores[idx]
    
    log.debug("Detected %i objects", labels.size)