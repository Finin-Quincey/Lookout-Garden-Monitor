import cv2
import numpy as np

WIDTH, HEIGHT = 1280, 720
THRESHOLD = 3

camera = cv2.VideoCapture(0)
camera.set(3, WIDTH)
camera.set(4, HEIGHT)

# Let the camera sensor settle for a few frames
for i in range(10):
    camera.read()

success, raw_frame = camera.read()
raw_frame = cv2.rotate(raw_frame, cv2.ROTATE_180)

cv2.imwrite("src/test_scripts/still_captures/raw.png", raw_frame)

# raw_frame = cv2.imread("example_dark_frame.png")

# Convert to YUV colour space
yuv = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2YUV)

print(np.unique(yuv[:, :, 0]))

cv2.imwrite("src/test_scripts/still_captures/y_channel.png", yuv[:, :, 0]) # Write Y channel to greyscale image

# Flatten pixels with lowest y-channel, i.e. luma/brightness to make the darkest areas uniform before equalising
yuv[:, :, 0][yuv[:, :, 0] < THRESHOLD] = 0
# Perform histogram equalisation on luma channel to improve image contrast
yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
# Convert back to BGR colour space
processed_frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

cv2.imwrite("src/test_scripts/still_captures/result.png", processed_frame)