activate(){
  . /home/pi/tflite/tflite-env/bin/activate
}

activate
python3 /home/pi/tflite/examples/TFLite_detection_webcam.py --modeldir=tflite/Sample_TFLite_model
sleep 10s
read -p "Press any key to exit"