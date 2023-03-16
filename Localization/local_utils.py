"""
Anna Anderson
UID: 105296576
180DA Capstone: Team 1 JAAK
Game: Guitar Hero
This script defines localization class utilities for detection
It utilizes cv2 to process webcam data.
Input: Camera data
Output: Order of players in multiplayer (colors relative to certain regions) or region of single player 

References:
https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_video_display/py_video_display.html
https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html 
https://pythonprogramming.net/color-filter-python-opencv-tutorial/
https://automaticaddison.com/real-time-object-tracking-using-opencv-and-a-webcam/ 
https://code.likeagirl.io/finding-dominant-colour-on-an-image-b4e075f98097 
https://www.geeksforgeeks.org/how-to-update-a-plot-in-matplotlib/ 
https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/ 

"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import paho.mqtt.client as mqtt

# 0. define callbacks - functions that run when events happen.
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe("ktanna/local", qos=1)
    print("Connection returned result: " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("ece180d/test")
    # The callback of the client when it disconnects.

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')


def find_histogram(clt):
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=numLabels)

    hist = hist.astype("float")
    hist /= hist.sum()

    return hist

# Returns low & high thresholds of a color
# For HSV, Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255]
def threshold(HSV, htol, stol, vtol): 
    low_threshold = list(HSV)
    high_threshold = list(HSV)

    # Get low threshold
    low_threshold[0] -= htol
    low_threshold[1] -= stol
    low_threshold[2] -= vtol
    if low_threshold[0] < 0:
        low_threshold[0] = 0
    if low_threshold[1] < 0:
        low_threshold[1] = 0
    if low_threshold[2] < 0:
        low_threshold[2] = 0
    
    # Get high threshold
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

def in_border_range(tol, x, x2, y, y2, w, h): # find if in the border range
    print('X ', x)
    print('GX ', x2)
    if (((x2 > (x)) and (x2 < (x + w + tol))) and ((y2 > (y)) and (y2 < (y + h + tol)))) or (((x2 < (x)) and (x2 > (x - tol))) and ((y2 < (y)) and (y2 > (y - tol)))):
        return True
    return False

# SINGLE PLAYER
def detect_position(colors, camera): # gives position of one color
    cap = cv2.VideoCapture(camera) # start webcam capture (0 for onboard camera, 1 for USB camera)
    # Perform thresholding
    c1_lower, c1_upper = threshold(colors['c1'], 5, 150, 150) # red
    border_lower, border_upper = threshold(colors['c2'], 5, 100, 100) # green

    tol = 5 # border tolerance
    atol = 500 # area tolerance

    # initialize MQTT values
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect_async('mqtt.eclipseprojects.io')
    client.loop_start()
    client.publish("ktanna/local", 1, qos =1)

    start = True # done calibrating

    # Start reading in orders
    while (start):
        # Reading the video from the webcam in image frames
        _, frame = cap.read()

        # Convert the frame in BGR(RGB color space) to HSV(hue-saturation-value) color space
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        kernel = np.ones((3, 3), np.uint8)

        # define masks
        red_mask = cv2.inRange(hsvFrame, np.array(c1_lower, np.uint8), np.array(c1_upper, np.uint8))
        red_mask = cv2.erode(red_mask, kernel, iterations=2)
        red_mask = cv2.dilate(red_mask, kernel, iterations=2)
        border_mask = cv2.inRange(hsvFrame, np.array(border_lower, np.uint8), np.array(border_upper, np.uint8))
        border_mask = cv2.erode(border_mask, kernel, iterations=2)
        border_mask = cv2.dilate(border_mask, kernel, iterations=2)
        #flip = cv2.flip(red_mask,1) # for testing purposes

        # Bools to store if we see a certain color:
        red = False
        

        rx = 0


        # Creating contour to track red color
        contours, hierarchy = cv2.findContours(red_mask,
                                            cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_SIMPLE)
        
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if(area > atol):
                x, y, w, h = cv2.boundingRect(contour)
                contours2, _ = cv2.findContours(border_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # detect green border
                for img, cnt in enumerate(contours2): 
                    x2, y2, w2, h2 = cv2.boundingRect(cnt) 
                    if in_border_range(tol, x, x2, y, y2, w, h): # if green border is in vicinity of the color square, we have properly detected color
                        rx = x
                        red = True
                        frame = cv2.rectangle(frame, (x, y), 
                                                (x + w, y + h), 
                                                (0, 0, 255), 2)
                        frame = cv2.rectangle(frame, (x2, y2), 
                                                (x2 + w2, y2 + h2), 
                                                (0, 255, 0), 2)
                        cv2.putText(frame, "Red Color", (x, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                                    (0, 0, 255))
        # Player position ranges between 0 and 640
        if red:
            position = 0
            if (rx < 160):
                position = 4
            elif(rx >= 160 and rx < 320):
                position = 3
            elif (rx >= 320 and rx < 480):
                position = 2
            else:
                position = 1
            print('Player position: ', position)
            position = str(position) + ',' + str(rx)
            client.publish("ktanna/local", position, qos=1) # publish on MQTT
        else:
            position = 'OOB' # out of bounds
            client.publish("ktanna/local", position, qos=1)  # publish on MQTT
        
        
        flip = cv2.flip(frame,1) # mirror frame for visual understanding
        cv2.putText(flip, "zone 1", (10, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 255, 0))
        cv2.putText(flip, "zone 2", (170, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 255, 0))
        cv2.putText(flip, "zone 3", (330, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 255, 0))
        cv2.putText(flip, "zone 4", (490, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 255, 0))
        line_thickness = 2
        cv2.line(flip, (160, 0), (160, 480), (0, 255, 0), thickness=line_thickness)
        cv2.line(flip, (320, 0), (320, 480), (0, 255, 0), thickness=line_thickness)
        cv2.line(flip, (480, 0), (480, 480), (0, 255, 0), thickness=line_thickness)
        cv2.imshow("Color Detection in Real-Time", flip)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

# MULTI-PLAYER
def detect_order(colors, camera): # gives position of 4 colors
    cap = cv2.VideoCapture(camera) # start webcam capture (0 for onboard camera, 1 for USB camera)
    # Perform thresholding
    c1_lower, c1_upper = threshold(colors['c1'], 5, 150, 170) # red
    c2_lower, c2_upper = threshold(colors['c2'], 2, 50, 50) # orange
    c3_lower, c3_upper = threshold(colors['c3'], 5, 50, 50) # blue
    c4_lower, c4_upper = threshold(colors['c4'], 5, 50, 50) # purple
    border_lower, border_upper = threshold(colors['c5'], 3, 50, 60) # green

    tol = 3 # border tolerance
    atol = 500 # area tolerance

    # initialize MQTT values
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect_async('mqtt.eclipseprojects.io')
    client.loop_start()
    client.publish("ktanna/local", 1, qos =1)

    start = True # done setting up

    # Start reading in orders
    while (start):
        # Reading the video from the webcam in image frames
        _, frame = cap.read()

        # Convert the frame in BGR(RGB color space) to HSV(hue-saturation-value) color space
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        kernel = np.ones((3, 3), np.uint8)

        # define masks
        red_mask = cv2.inRange(hsvFrame, np.array(c1_lower, np.uint8), np.array(c1_upper, np.uint8))
        red_mask = cv2.erode(red_mask, kernel, iterations=2)
        red_mask = cv2.dilate(red_mask, kernel, iterations=2)

        orange_mask = cv2.inRange(hsvFrame, np.array(c2_lower, np.uint8), np.array(c2_upper, np.uint8))
        orange_mask = cv2.erode(orange_mask, kernel, iterations=2)
        orange_mask = cv2.dilate(orange_mask, kernel, iterations=2)

        blue_mask = cv2.inRange(hsvFrame, np.array(c3_lower, np.uint8), np.array(c3_upper, np.uint8))
        blue_mask = cv2.erode(blue_mask, kernel, iterations=2)
        blue_mask = cv2.dilate(blue_mask, kernel, iterations=2)

        purple_mask = cv2.inRange(hsvFrame, np.array(c4_lower, np.uint8), np.array(c4_upper, np.uint8))
        purple_mask = cv2.erode(purple_mask, kernel, iterations=2)
        purple_mask = cv2.dilate(purple_mask, kernel, iterations=2)

        border_mask = cv2.inRange(hsvFrame, np.array(border_lower, np.uint8), np.array(border_upper, np.uint8))
        border_mask = cv2.erode(border_mask, kernel, iterations=2)
        border_mask = cv2.dilate(border_mask, kernel, iterations=2)
        # flip = cv2.flip(border_mask,1) # for testing purposes

        # Bools to store if we see a certain color:
        red = False
        orange = False
        blue = False
        purple = False

        rx, ox, bx, px = 0, 0, 0, 0


        # Creating contour to track red color
        contours, hierarchy = cv2.findContours(red_mask,
                                            cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_SIMPLE)
        
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if(area > atol):
                x, y, w, h = cv2.boundingRect(contour)
                contours2, _ = cv2.findContours(border_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # detect green border
                for img, cnt in enumerate(contours2): 
                    x2, y2, w2, h2 = cv2.boundingRect(cnt) 
                    if in_border_range(tol, x, x2, y, y2, w, h): # if green border is in vicinity of the color square, we have properly detected color
                        rx = x
                        red = True
                        frame = cv2.rectangle(frame, (x, y), 
                                                (x + w, y + h), 
                                                (0, 0, 255), 2)
                        cv2.putText(frame, "Red Color", (x, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                                    (0, 0, 255))
                        
        # Creating contour to track orange color
        contours, hierarchy = cv2.findContours(orange_mask,
                                            cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_SIMPLE)

        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if(area > atol):
                x, y, w, h = cv2.boundingRect(contour)
                contours2, _ = cv2.findContours(border_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                for img, cnt in enumerate(contours2): 
                    x2, y2, w2, h2 = cv2.boundingRect(cnt)
                    if in_border_range(tol, x, x2, y, y2, w, h):
                        ox = x
                        orange = True
                        frame = cv2.rectangle(frame, (x, y), 
                                                (x + w, y + h),
                                                (0, 164, 255), 2)
                        
                        cv2.putText(frame, "Orange Color", (x, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 
                                    1.0, (0, 164, 255))

        # Creating contour to track blue color
        contours, hierarchy = cv2.findContours(blue_mask,
                                            cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_SIMPLE)
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if(area > atol):
                x, y, w, h = cv2.boundingRect(contour)
                contours2, _ = cv2.findContours(border_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                for img, cnt in enumerate(contours2): 
                    x2, y2, w2, h2 = cv2.boundingRect(cnt)
                    if in_border_range(tol, x, x2, y, y2, w, h):
                        bx = x
                        blue = True
                        frame = cv2.rectangle(frame, (x, y),
                                                (x + w, y + h),
                                                (255, 0, 0), 2)
                        
                        cv2.putText(frame, "Blue Color", (x, y),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1.0, (255, 0, 0))
                        
        # Creating contour to track purple color
        contours, hierarchy = cv2.findContours(purple_mask,
                                            cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_SIMPLE)

        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if(area > atol):
                x, y, w, h = cv2.boundingRect(contour)
                contours2, _ = cv2.findContours(border_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                for img, cnt in enumerate(contours2): 
                    x2, y2, w2, h2 = cv2.boundingRect(cnt)
                    if in_border_range(tol, x, x2, y, y2, w, h):
                        px = x
                        purple = True
                        frame = cv2.rectangle(frame, (x, y), 
                                                (x + w, y + h),
                                                (245, 0, 147), 2)
                        
                        cv2.putText(frame, "Purple Color", (x, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 
                                    1.0, (245, 0, 147))

        order = {'r':rx, 'o':ox,'b':bx, 'p':px }

        if red and orange and purple and blue:
            order = dict(sorted(order.items(), key=lambda x:x[1], reverse=True))
            color_order = list(order.keys())
            print('Color order is: ', color_order)
            position = ''
            for i in np.arange(len(color_order)):
                position += str(i+1) + color_order[i] + ' '
            client.publish("ktanna/local", position, qos=1) # publish on MQTT
        
        flip = cv2.flip(frame,1) # mirror frame for visual understanding
        cv2.imshow("Multiple Color Detection in Real-Time", flip)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
