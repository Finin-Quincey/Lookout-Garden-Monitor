# 🦊 Lookout Garden Monitor

Code for my final year project (MIDP module, year 4 IDE) to design and build a device for deterring unwanted animals from urban gardens. This repository contains the Python code (located under `src`) that runs on a Raspberry Pi inside the prototype device, performing object recognition on the video feed from the camera to determine which animals are present and decide whether to activate the deterrent. For an in-depth description of how the software operates, see the [activity diagram](https://github.com/Finin-Quincey/Lookout-Garden-Monitor/blob/main/images/activity_diagram.png) and [state diagram](https://github.com/Finin-Quincey/Lookout-Garden-Monitor/blob/main/images/state_diagram_simple.png).

_This project won the [IMechE Mechatronics Engineering Student of the Year Award](https://www.imeche.org/industry-sectors/mechatronics-informatics-and-control/about-the-mechatronics-informatics-and-control-group/mechatronics-engineering-student-of-the-year-competition) 2022!_

![](https://github.com/Finin-Quincey/Lookout-Garden-Monitor/blob/main/images/banner.jpg)

## 🐈 Specs

### Hardware
- Raspberry Pi 3B
- Ansmann 20.8Ah USB power bank
- SimplyTronics ST-00081 PIR sensor module
- Arducam OV5647 5MP motorised IR-CUT camera (day & night vision)
- 86dB piezo transducer buzzer
- Custom veroboard PCB (see [schematic](https://github.com/Finin-Quincey/Lookout-Garden-Monitor/blob/main/images/schematic.png))
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
- [OpenCV Python Tutorials](https://docs.opencv.org/4.4.0/d6/d00/tutorial_py_root.html)
- [TensorFlow Model Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf1_detection_zoo.md#mobile-models)
- [pigpio Reference](http://abyz.me.uk/rpi/pigpio/python.html)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [Interactive simulation of the buzzer driver circuit](http://www.falstad.com/circuit/circuitjs.html?ctz=CQAgjCCsB0AM8MUgLAUwLQA4TOgNgCYw8BmEwsSTATgOWp2wHYpYoMwwAoAMxCczIQBWM0HDIeHGwIhYcTFwA2IErCEFJq9eDCy28hJRDpDTasljViyAnmSQmEbgGNpbTrMsemUj9EwSAgwWMGgLKlpiXwISSFg6OThYbgBzEEFsTSlM4UxsAy4Ad20hT3ddfWLSiSlvWrkuABMoPBktPC1s4RAm1B4AQwBXJQAXLgAPKAFhERBSGUsccCEAISUAexcAawBLADtUgB0j-YARXY2+ybyhJkhVSAYZsuwAeQBnF12lJQHRjYAJxuyDAPi8kBI4FoyzAQgACrtUAAvDYnfarIbI5GoYFTTB6YS2DJMRYPMpCACybwAygAxACiABUuAAlaGycpwsqEgzSKByQXySBs+ZMTmEtrYcoybQIcD4B5hTpC6AikqYeANXLdWDVerdZCahp6wH8cR6MQaUSCsHwLgAB0Y7Tqxq5Qv1WvKRo8vK4ZoEZQI2Ew9nAwdtiC46VDQZDYeIfL1JU6Um6viyWj1U3s0uQUjwhBWDCDcgAajdSFIwCQIIXOSQhKW6Zt-tUmORw1au410nhxSshP3Ob4PTT+J3LWLORHZYMlB9UIKSDcqMwHrnzbDsABxeEASTeRw+yErZHAsA3pAv2FLAGFNjt-c6GpIXYKCARmhzKjVyrI+kGEZxjNeowFHA0s3DLgACNVHMcMSyLOgIGzYRYBYY1NAYO1YTWR89kOdELiuVAQWoFhgzYSAjTlPCQCZIZ9gOY5TlZVAPl2D4ATxHACGeB5ICoLdXhAHhjyOABHY8wGPAB6Y8AAoCEAAeBACwiRSABk7wASh02DpgYSBZHuGQUkaOCCCYIRjOmCBa0KDZwx6NgHFgQtVGgKFDHgVDVGcqFiEaEhpVkKFNHlOJ5TpQFUEkoZUH2FwAE8uBClzwAvLU7wGB0Bm+UYBiSsj0r85x5X3fYmiGFweLS7BG0y8qtQZeL-kufZ6syzksrYSrqtqoqXBK6Uyt6kAyw2MYBlSEbbSa+VqXpZkusJHq7TYB8tm2VaCgWrV4RGJR0CaDYin2Y92M47igS62d9rYRjmKIj4rq4ur0rUeaNpASrRlxfYBiUS6OPeoayKAA)
