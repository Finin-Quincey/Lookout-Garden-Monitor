"""
Camera Manager

This module is responsible for interacting with the camera, grabbing and storing frames, saving videos and displaying the
camera feed on-screen in development mode.

Author: Finin Quincey

Based on the example script TFLite_detection_webcam.py by Evan Juras:
https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/TFLite_detection_webcam.py
"""

import logging as log
import os           # Operating system commands
import time         # Timing functions
import cv2          # OpenCV functions
import numpy as np  # Matrix operations

### Constants ###

CAMERA_INDEX  = 0                # Index of the camera to use (there is only one camera so this will always be 0)
WIDTH, HEIGHT = 1280, 720        # Image dimensions in pixels
RESOLUTION    = (WIDTH, HEIGHT)  # Tuple version for convenience
WINDOW_TITLE  = "Camera Preview" # Title of the preview window when in developer mode
        
### Setup ###

log.info("Initialising camera")

# Initialise camera
stream = cv2.VideoCapture(CAMERA_INDEX)
stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
stream.set(3, WIDTH)
stream.set(4, HEIGHT)

# Read first frame from the stream
success, raw_frame = stream.read()

if not success:
    log.warn("Failed to retrieve current frame from camera")

### Functions ###
    
def pause():
    """
    Closes the camera and releases the resources it was using.
    """
    log.info("Closing camera stream")
    global stream
    stream.release()

def resume():
    """
    Reopens the camera after it has been paused.
    """
    log.info("Opening camera stream")
    global stream
    stream.open(CAMERA_INDEX)
    
def shutdown():
    """
    Closes the camera, releases the resources it was using and closes any open windows
    """
    log.info("Closing open windows")
    cv2.destroyAllWindows()
    pause()

def capture_frame():
    """
    Captures the next frame from the camera.
    """
    global stream
    global raw_frame
    success, raw_frame = stream.read()
    if not success:
        log.warn("Failed to retrieve current frame from camera")

def annotate_current(boxes, classes, scores):
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
        if ((scores[i] > CONFIDENCE_THRESHOLD) and (scores[i] <= 1.0)):

            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1,(boxes[i][0] * HEIGHT)))
            xmin = int(max(1,(boxes[i][1] * WIDTH)))
            ymax = int(min(imH,(boxes[i][2] * HEIGHT)))
            xmax = int(min(imW,(boxes[i][3] * WIDTH)))
            
            cv2.rectangle(annotated_frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

            # Draw label
            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            cv2.rectangle(annotated_frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            cv2.putText(annotated_frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

    # Draw framerate in corner of frame
    #cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

    # All the results have been drawn on the frame, so it's time to display it.
    #cv2.imshow('Object detector', frame)
    
def display_current():
    """
    Displays the current frame with annotations
    """
    global raw_frame # Using raw frame for debugging purposes
    cv2.imshow(WINDOW_TITLE, raw_frame)
    #global annotated_frame
    #cv2.imshow(WINDOW_TITLE, annotated_frame)