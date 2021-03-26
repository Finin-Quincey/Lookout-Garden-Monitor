# 🦊 Lookout Garden Monitor
Code for my final year project (MIDP module, year 4 IDE) to design and build a device for deterring unwanted animals from urban gardens. This repository contains the Python code that runs on a Raspberry Pi inside the prototype device, performing object recognition on the video feed from the camera to determine which animals are present and decide whether to activate the deterrent.

## 🐈 Specs

### Hardware
- Raspberry Pi 3B
- Ansmann 20.8Ah USB power bank
- SimplyTronics ST-00081 PIR sensor module
- Arducam OV5647 5MP motorised IR-CUT camera (day & night vision)
- 86dB piezo transducer buzzer
- Custom veroboard PCB (see schematic)
- Custom 3D-printed water-resistant housing with velcro straps for mounting

### Software
- Raspbian Buster
- Python 3.7.3
- TensorFlow Lite 2.6
- OpenCV 3.4.6
- pigpio 1.78

## 🐾 Useful Links
- [Installing TensorFlow Lite on Raspberry Pi](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md)
- [Object Detection with TensorFlow Lite](https://www.tensorflow.org/lite/examples/object_detection/overview)
- [TensorFlow Model Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf1_detection_zoo.md#mobile-models)
- [pigpio Reference](http://abyz.me.uk/rpi/pigpio/python.html)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
