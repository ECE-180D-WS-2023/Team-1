"""
Anna Anderson
UID: 105296576
180DA Capstone: Team 1 JAAK
Game: Guitar Hero
This script will be utilized for locating players based on color in accordance with our game.
It utilizes cv2 to process webcam data.
Input: Camera data
Output: Order of players (colors relative to certain regions)

References:
https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_video_display/py_video_display.html
https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html 
https://pythonprogramming.net/color-filter-python-opencv-tutorial/
https://automaticaddison.com/real-time-object-tracking-using-opencv-and-a-webcam/ 
https://code.likeagirl.io/finding-dominant-colour-on-an-image-b4e075f98097 
https://www.geeksforgeeks.org/how-to-update-a-plot-in-matplotlib/ 
https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/ 

Only calibrating for red for this example
"""
import cv2
import numpy as np

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Helper functions
# ===========================================================================================
def find_histogram(clt):
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=numLabels)

    hist = hist.astype("float")
    hist /= hist.sum()

    return hist

def plot_colors2(hist, centroids):
    bar = np.zeros((50, 300, 3), dtype="uint8")
    startX = 0
    for (percent, color) in zip(hist, centroids):
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                      color.astype("uint8").tolist(), -1)
        startX = endX
    # return the bar chart
    return bar

# resturns low & high thresholds of a color
def threshold(HSV, htol, stol, vtol): 
    # For HSV, Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255].
    low_threshold = list(HSV)
    high_threshold = list(HSV)

    low_threshold[0] -= htol
    low_threshold[1] -= stol
    low_threshold[2] -= vtol

    if low_threshold[0] < 0:
        low_threshold[0] = 0
    if low_threshold[1] < 0:
        low_threshold[1] = 0
    if low_threshold[2] < 0:
        low_threshold[2] = 0
    
    high_threshold[0] += htol
    high_threshold[1] += stol
    high_threshold[2] += vtol
    if high_threshold[0] > 179:
        high_threshold[0] = 179
    if high_threshold[1] > 255:
        high_threshold[1] = 255
    if high_threshold[2] > 255:
        high_threshold[2] = 255

    return low_threshold, high_threshold
    
# ===========================================================================================

calibrated = False
color = 0
colors = {} # dict to store colors
cap = cv2.VideoCapture(0) # start webcam capture (0 for onboard camera, 1 for USB camera)

print("Please calibrate in the order Red, Orange, Green, Blue ******************")
print("Press 'c' to enter color")

while color < 2:
    # Capture frame-by-frame
    ret, frame = cap.read()
    converted = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # convert frame to HSV
    # create square of interest on screen
    central_x = len(frame)//2
    central_y = len(frame[1])//2
    x_s = central_x - 25
    y_s = central_y - 25
    cv2.rectangle(frame,(x_s,y_s),(x_s + 50,y_s + 50),(0,255,0),3)
    flip = cv2.flip(frame,1)
    cv2.imshow('frame', flip) # show augmented frame
    # determine dominant color in square of interest
    img = frame[y_s + 3:y_s + 44, x_s + 3:x_s+44] # exclude drawn square
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.reshape((img.shape[0] * img.shape[1],3)) #represent as row*column,channel number
    clt = KMeans(n_clusters=3) #KMeans
    clt.fit(img)
    # Print RGB / HSV values
    RGB_vals = clt.cluster_centers_.astype('uint8')
    HSV_vals = cv2.cvtColor(np.array([RGB_vals]), cv2.COLOR_RGB2HSV) # convert to HSV
    # print("RGB for 3 clusters:\n", clt.cluster_centers_)
    #print("\nHSV for 3 clusters:\n", HSV_vals)
    if cv2.waitKey(1) & 0xFF ==ord('c'): # user inputs 'c' to trigger when object is in box
        print("Color input: ", color + 1, "HSV: ", HSV_vals)
        # plot histogram
        color_key = 'c' + str(color+1)
        colors[color_key] = HSV_vals[0][0]
        color += 1
        # update plot
print(colors)

# tolerances for thresholding, can be changed
htol = 5
stol = 25
vtol = 25

c1_lower, c1_upper = threshold(colors['c1'], htol, stol, vtol) # red
c2_lower, c2_upper = threshold(colors['c2'], htol, stol, vtol)

tol = 10
calibrated = True

while (calibrated):
    _, frame = cap.read()
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsvFrame, np.array(c1_lower, np.uint8), np.array(c1_upper, np.uint8))
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)

    mask_2 = cv2.inRange(hsvFrame, np.array(c2_lower, np.uint8), np.array(c2_upper, np.uint8))
    mask_2 = cv2.erode(mask, kernel, iterations=2)
    mask_2 = cv2.dilate(mask, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if(area > 1000):
            red = True
            x, y, w, h = cv2.boundingRect(contour)
            contours2, con2 = cv2.findContours(mask_2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for pi, cnt in enumerate(contours2): #to_do make the sheet black around the eadges
                x2, y2, w2, h2 = cv2.boundingRect(cnt)
                if x2 > x - tol:
                    print('green')
                    rx = x
                    frame = cv2.rectangle(frame, (x, y), 
                                            (x + w, y + h), 
                                            (0, 0, 255), 2)
                    
                    cv2.putText(frame, "Red Color", (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                                (0, 0, 255))
                frame = cv2.rectangle(frame, (x2, y2), 
                                        (x2 + w2, y2 + h2), 
                                        (0, 255, 0), 2)
                    
                cv2.putText(frame, "Green Color", (x2, y2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                            (0, 0, 255))
    
        # area = cv2.contourArea(cnt)
        # epsilon = 0.1*cv2.arcLength(cnt,True)
        # approx = cv2.approxPolyDP(cnt,epsilon,True)
        # # approx = cv2.approxPolyDP(cnt, 0.02*cv2.arcLength(cnt, True), True)
        # x = approx.ravel()[0]
        # y = approx.ravel()[1]

        # if area > 400:
        #     cv2.drawContours(frame, [approx], 0, (0, 0, 0), 5)
        #     if len(approx) == 3:
        #         cv2.putText(frame, "Triangle", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        #     elif len(approx) == 4:
        #         cv2.putText(frame, "Rectangle", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        #     elif 10 < len(approx) < 20:
        #         cv2.putText(frame, "Circle", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
    
    # flip = cv2.flip(mask_2,1) # mirror frame for visual understanding
    flip = cv2.flip(frame,1) 
    cv2.imshow("Multiple Color Detection in Real-Time", flip)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()