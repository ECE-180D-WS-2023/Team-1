"""
Anna Anderson
UID: 105296576
180DA Capstone: Team 1 JAAK
Game: Guitar Hero
This script defines localization class
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
from local_utils import *

class localize:
    """
    Members:
        - players: number of players (1 or 4)
        - calibrated: bool determining calibration # initialized as False
        - color: number of colors involved in the game (# player + 1)
        - colors: dict storing the HSV color values
        - camera: camera type used for localization (0 for laptop webcam, 1 for USB camera)
        - positions:
    Methods:
        - __init__(self, players=None, camera=None): 
            initilize with players (can be 1 or 4, default is 4)
            initialize with camera type (default type is USB camera=1)
        - calibrate(self, recalibrate=None): calibrate colors with camera
            do not need to explictly call unless colors need to be recalibrated (set recalibrate=True)
            otherwise, automatically called from detect if not already calibrated
        - detect(self)
            detect color information
    """
    def __init__(self, players=None, camera=None, verbose = None):
        if players == None or players == 1:
            self.players = 1 # default single player
        elif players == 2: 
            self.players = 2 # otherwise multiplayer
        else:
            raise Exception("Not a valid number of players")
        self.calibrated = False # not yet calibrated
        self.color = self.players + 1
        self.colors = {}
        if camera == None or camera == 1:
            self.camera = 1 # default to USB camera
        else:
            self.camera = 0 # otherwise 
        if verbose == None or verbose == False:
            self.verbose = False
        elif verbose == True:
            self.verbose = True

    def calibrate(self, recalibrate=None): 
        if self.calibrated:
            if recalibrate == None or recalibrate == False:
                raise Exception("Not in recalibration mode")
            else:
                if recalibrate:
                    print("Recalibrating colors")
        else:
            print("Calibrating colors")
        # start webcam capture (0 for onboard camera, 1 for USB camera)
        cap = cv2.VideoCapture(self.camera) 
        color = 0

        while color < self.color:
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            # Capture frame-by-frame
            _, frame = cap.read()
            flip = cv2.flip(frame,1)

            # create square of interest on screen
            central_x = 320
            central_y = 240
            x_s = central_x - 25
            y_s = central_y - 25
            cv2.rectangle(flip,(x_s,y_s),(x_s + 50,y_s + 50),(0,255,0),3)

            # Print on screen to show calibration instructions
            if color == 0:
                cv2.putText(flip, "Red Color", (300, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                                        (0, 0, 255))
            if color == 1:
                if self.players == 2: # if multiplayer
                    cv2.putText(flip, "Blue Color", (300, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        1.0, (255, 0, 0))
                else: # if single player, only need one more color - the border color
                    cv2.putText(flip, "Green Border Color", (300, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 
                                        1.0, (0, 255, 0))
            if color == 2:
                cv2.putText(flip, "Green Border Color", (300, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 
                                        1.0, (0, 255, 0))

            cv2.imshow('Calibrate by aligning color card with central square & striking c', flip) # show mirrored frame

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
                self.colors[color_key] = HSV_vals[0][0]
                color += 1
        
        print("Colors collected")
        print(self.colors)
        self.calibrated=True
        cap.release()
        cv2.destroyAllWindows()
    
    def detect(self):
        if not self.calibrated:
            self.calibrate()
        if self.players == 1:
            detect_position(self.colors, self.camera)
        else:
            if self.verbose == True:
                detect_position_2(self.colors, self.camera, True)
            else:
                detect_position_2(self.colors, self.camera)