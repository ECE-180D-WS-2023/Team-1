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
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def find_histogram(clt):
    """
    create a histogram with k clusters
    :param: clt
    :return:hist
    """
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

calibrated = False
color = 0
# Precalibration initialize color arrays for HSV values
colors = {'c1':np.zeros(3), 'c2':np.zeros(3), 'c3':np.zeros(3), 'c4':np.zeros(3)}
cap = cv2.VideoCapture(1) # start webcam capture
plt.ion() # enable interactivity
fig = plt.figure()
ax = fig.add_subplot(111)

while color < 4:
    # Capture frame-by-frame
    ret, frame = cap.read()
    converted = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # convert frame to HSV
    # create square of interest on screen
    central_x = len(frame)//2
    central_y = len(frame[1])//2
    x_s = central_x - 25
    y_s = central_y - 25
    cv2.rectangle(frame,(x_s,y_s),(x_s + 50,y_s + 50),(0,255,0),3)
    cv2.imshow('frame', frame) # show augmented frame
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
        color_key = 'c' + chr(color+1)
        colors[color_key] = HSV_vals
        color += 1
        # update plot

thresh = {'l1':colors['c1'] - 10, 'u1':colors['c1'] + 10, 'l2':colors['c2'] - 10, 'u2':colors['c2'] + 10,'l3':colors['c3'] - 10, 'u3':colors['c3'] + 10,'l4':colors['c4'] - 10, 'u4':colors['c4'] + 10}

calibrated = True
print("Calibration finished!")


while(calibrated):
    # Listen for user input to quit program
    if cv2.waitKey(1) & 0xFF ==ord('q'):
        break

    # Capture frame-by-frame
    ret, frame = cap.read()

    converted = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #convert frame to HSV

    # Detect different colors
    detect1 = cv2.inRange(converted, thresh['l1'], thresh['u1'])
    detect2 = cv2.inRange(converted, thresh['l2'], thresh['u2'])
    detect3 = cv2.inRange(converted, thresh['l3'], thresh['u3'])
    detect4 = cv2.inRange(converted, thresh['l4'], thresh['u4'])

    # Morphological Transform, Dilation
    # for each color and bitwise_and operator
    # between frame and mask determines
    # to detect only that particular color
    kernal = np.ones((5, 5), "uint8")
      
    # For color 1
    c1_mask = cv2.dilate(detect1, kernal)
    res_c1 = cv2.bitwise_and(frame, frame, 
                              mask = c1_mask)
      
    # For color 2
    c2_mask = cv2.dilate(detect2, kernal)
    res_c2 = cv2.bitwise_and(frame, frame,
                                mask = c2_mask)
      
    # For color 3
    c3_mask = cv2.dilate(detect3, kernal)
    res_c3 = cv2.bitwise_and(frame, frame,
                               mask = c3_mask)

    # For color 4
    c4_mask = cv2.dilate(detect4, kernal)
    res_c3 = cv2.bitwise_and(frame, frame,
                               mask = c3_mask)
   
    # Creating contour to track color 1
    contours, hierarchy = cv2.findContours(c1_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
      
    for pic, contour in enumerate(contours):
        #area = cv2.contourArea(contour)
        
        x, y, w, h = cv2.boundingRect(contour)
        frame = cv2.rectangle(frame, (x, y), 
                                    (x + w, y + h), 
                                    (0, 0, 255), 2)
            
        cv2.putText(frame, "Color 1", (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    (0, 0, 255))    
  
    # Creating contour to track color 2
    contours, hierarchy = cv2.findContours(c2_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
      
    for pic, contour in enumerate(contours):
        #area = cv2.contourArea(contour)
        
        x, y, w, h = cv2.boundingRect(contour)
        frame = cv2.rectangle(frame, (x, y), 
                                    (x + w, y + h),
                                    (0, 255, 0), 2)
            
        cv2.putText(frame, "Color 2", (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1.0, (0, 255, 0))
  
    # Creating contour to track color 3
    contours, hierarchy = cv2.findContours(c3_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        #area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        frame = cv2.rectangle(frame, (x, y),
                                    (x + w, y + h),
                                    (255, 0, 0), 2)
            
        cv2.putText(frame, "Color 3", (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (255, 0, 0))

    # Creating contour to track color 4
    contours, hierarchy = cv2.findContours(c4_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        #area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        frame = cv2.rectangle(frame, (x, y),
                                    (x + w, y + h),
                                    (255, 0, 0), 2)
            
        cv2.putText(frame, "Color 4", (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (255, 0, 0))
              
    # Program Termination
    cv2.imshow("Multiple Color Detection in Real-TIme", frame)
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()