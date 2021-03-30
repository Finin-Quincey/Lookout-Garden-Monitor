"""
Camera Manager

This module is responsible for interacting with the camera, grabbing and storing frames, saving videos and displaying the
camera feed on-screen in development mode.

Author: Finin Quincey

Based on the example script TFLite_detection_webcam.py by Evan Juras:
https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/TFLite_detection_webcam.py
"""

import logging as log          # Log messages and log file output
import os                      # Operating system commands
import time                    # Timing functions
from datetime import datetime  # Real-world date and time
import cv2                     # OpenCV functions
import numpy as np             # Matrix operations

### Constants ###

CAMERA_INDEX  = 0                # Index of the camera to use (there is only one camera so this will always be 0)
WIDTH, HEIGHT = 1280, 720        # Image dimensions in pixels
RESOLUTION    = (WIDTH, HEIGHT)  # Tuple version for convenience
WINDOW_TITLE  = "Camera Preview" # Title of the preview window when in developer mode
FRAMERATE     = 20               # Target framerate to capture at, in frames per second
TEXT_COLOUR   = (255, 255, 255)  # Colour of the text at the top of the frame

INACTIVE_SCREEN = np.zeros((WIDTH, HEIGHT, 3)) # Just a black screen for now

### Setup ###

log.info("Initialising camera")

# Initialise module variables
raw_frame = INACTIVE_SCREEN
annotated_frame = INACTIVE_SCREEN

# Initialise camera object
stream = cv2.VideoCapture()

# Open preview window
cv2.namedWindow(WINDOW_TITLE)
cv2.imshow(WINDOW_TITLE, INACTIVE_SCREEN)

# Initialise video writer
codec = cv2.VideoWriter_fourcc(*"XVID")
writer = cv2.VideoWriter(f"{os.getcwd()}/captures/{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.avi", codec, FRAMERATE, RESOLUTION)

# TODO: Make this a queue and write frames in a separate thread so the RAM doesn't fill up so quickly
frame_buffer = [] # Stores the captured frames to be written to disk later

### Functions ###

def open():
    """
    Opens the camera stream.
    """
    log.info("Opening camera stream")
    global stream
    stream.open(CAMERA_INDEX)
    # For some reason this introduces a delay when capturing the frame, it seems to work okay without it though
    #stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    stream.set(3, WIDTH)
    stream.set(4, HEIGHT)
    
def close():
    """
    Closes the camera stream, saves the video and releases the resources it was using.
    """
    log.info("Closing camera stream")
    global stream
    stream.release()
    
    log.info("Writing buffered frames to file")
    global writer
    global frame_buffer
    i = 1
    for frame in frame_buffer:
        writer.write(frame)
        log.debug("Writing frame %i of %i", i, len(frame_buffer))
        i += 1
    frame_buffer = []
    log.info("Closing file")
    #writer.release()
    
def shutdown():
    """
    Closes the camera, releases the resources it was using, saves any frames in memory and closes any open windows
    """
    log.info("Closing open windows")
    cv2.destroyAllWindows()
    close()
    cv2.waitKey(1) # Required to get opencv to update (must be last it seems)

def capture_frame():
    """
    Captures the next frame from the camera.
    """
    global stream
    global raw_frame
    success, raw_frame = stream.read()
    raw_frame = cv2.rotate(raw_frame, cv2.ROTATE_180)
    if not success:
        log.warn("Failed to retrieve current frame from camera")

def annotate_current(boxes, labels, scores):
    """
    Annotates the current frame with labels representing the given detected objects and their locations.
    """
    # Take a copy of the raw frame
    # We need to take care not to modify the raw frame because we can't guarantee when the object detector thread will
    # access it, and we don't want it performing object detection on the annotated frame
    global annotated_frame
    annotated_frame = raw_frame.copy()
    
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):

        # Get bounding box coordinates and draw box
        # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
        ymin = int(max(1,(boxes[i][0] * HEIGHT)))
        xmin = int(max(1,(boxes[i][1] * WIDTH)))
        ymax = int(min(HEIGHT,(boxes[i][2] * HEIGHT)))
        xmax = int(min(WIDTH,(boxes[i][3] * WIDTH)))
        
        cv2.rectangle(annotated_frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)

        # Draw label
        object_name = labels[i] # Look up object name from "labels" array using class index
        label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
        label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
        cv2.rectangle(annotated_frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
        cv2.putText(annotated_frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

    # Date and time
    cv2.putText(annotated_frame, f"{datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOUR, 1, cv2.LINE_AA)

    # Draw framerate in corner of frame
    #cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
    
def display_current():
    """
    Displays the current frame with annotations
    """
    global annotated_frame
    cv2.imshow(WINDOW_TITLE, annotated_frame)
    
def store_current():
    """
    Stores the current frame to the video output
    """
    global annotated_frame
    global frame_buffer
    frame_buffer.append(annotated_frame)