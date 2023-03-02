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

"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Start of Helper Functions
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

def in_border_range(tol, x, x2, y, y2, w, h):
    if ((x2 > (x - tol)) and (x2 < (x + w + tol))) and ((y > (y- tol)) and (y < (y + h + tol))):
        return True
    return False
    
# End of Helper Functions
# ===========================================================================================

calibrated = False
colors = {} # dict to store colors
cap = cv2.VideoCapture(1) # start webcam capture (0 for onboard camera, 1 for USB camera)

print("Please calibrate in the order Red, Orange, Blue, Purple, Green (for border) ******************")
print("Press 'c' to enter color")

# Calibration phase 
color = 0
while color < 5:
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
    cv2.imshow('frame', flip) # show mirrored frame

    # determine dominant color in square of interest
    img = frame[y_s + 3:y_s + 44, x_s + 3:x_s+44] # exclude drawn square
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.reshape((img.shape[0] * img.shape[1],3)) #represent as row*column,channel number
    clt = KMeans(n_clusters=3) #KMeans
    clt.fit(img)
    RGB_vals = clt.cluster_centers_.astype('uint8')
    HSV_vals = cv2.cvtColor(np.array([RGB_vals]), cv2.COLOR_RGB2HSV) # convert to HSV

    # user inputs 'c' to trigger when object is in box
    if cv2.waitKey(1) & 0xFF ==ord('c'): 
        print("Color input: ", color + 1, "HSV: ", HSV_vals)
        color_key = 'c' + str(color+1)
        colors[color_key] = HSV_vals[0][0]
        color += 1
        if (color == 5):
            print("Input green border color")

print("Colors collected")
print(colors)

# tolerances for thresholding, can be changed
htol = 2
stol = 50
vtol = 50
orange_hue_tol = 3 # found that orange can get confused with skin tone, give lower threshold

# Perform thresholding
c1_lower, c1_upper = threshold(colors['c1'], 5, 150, 170) # red
c2_lower, c2_upper = threshold(colors['c2'], 2, 50, 50) # orange
c3_lower, c3_upper = threshold(colors['c3'], 5, 50, 50) # blue
c4_lower, c4_upper = threshold(colors['c4'], 5, stol, vtol) # purple
border_lower, border_upper = threshold(colors['c5'], 3, 50, 60) # green

tol = 3 # border tolerance
atol = 500 # area tolerance

calibrated = True # done calibrating

# Start reading in orders
while (calibrated):
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
     
    flip = cv2.flip(frame,1) # mirror frame for visual understanding
    cv2.imshow("Multiple Color Detection in Real-Time", flip)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()