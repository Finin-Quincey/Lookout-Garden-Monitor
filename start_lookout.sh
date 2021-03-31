#!/bin/bash

sudo pigpiod

activate(){
  . /home/pi/tflite/tflite-env/bin/activate
}

activate
python3 /home/pi/tflite/src/lookout.py
sleep(10)