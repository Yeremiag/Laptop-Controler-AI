import cv2
import mediapipe as mp
import pyautogui
import numpy as np 
import screen_brightness_control as sbc
from screen_brightness_control import get_brightness
from screen_brightness_control import set_brightness
from pynput.mouse import Button, Controller

#Function to extract x and y coordinate of the hand landmark 
def cx(x):
    if results.multi_hand_landmarks:
        return results.multi_hand_landmarks[0].landmark[x].x*image_width

def cy(y):
    if results.multi_hand_landmarks:
        return results.multi_hand_landmarks[0].landmark[y].y*image_height

#Setting up User Guide Manual image by importing it into the variable
path = r'C:\Users\yereg\Downloads\Lock.png'
lock = cv2.imread(path)
im = cv2.imread('Lock.png') 

#Putting some mediapipe functions into variables
mp_drawing_styles = mp.solutions.drawing_styles
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

#Setting up video and the resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

#Some variables for controlling volume, brigtness, cursor, etc
flag, flag1, flag3, flagb, flagb2, flagc = True, True, True, True, False, False
volumec, mute, unmute, brightnessc, cursor = True, True, True, True, True
cx8, cy8, cy8_, dcy8, cx20, cy20, cx20_, dcx20= 0,0,0,0,0,0,0,0
counter, counter2 = 0, 0
mute, mute2 = 1, 0
volume = 0
brightness = 0
mouse = Controller()

with mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.5,min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    #Mirroring our webcam
    image = cv2.cvtColor(cv2.flip(image, 1),1)
    image.flags.writeable = False
    #Setting the video color as in the real world
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    #Getting our webcam resolution
    image_height, image_width, _ = image.shape
    image.flags.writeable = True
    
    if results.multi_hand_landmarks:
        volume = 0
        flag = True

        #Getting the x and y coordinate difference of our point finger to decrease/increase the volume
        cx8, cy8 = cx(8), cy(8)
        if flag1:
            cy8_ = cy8
            flag1 = False
        dcy8 = cy8 - cy8_
        cy8_ = cy8
        flag3 = True
        
        #Getting the x and y coordinate difference of our pinky finger to decrease/increase the brightness
        cx20, cy20 = cx(20), cy(20)
        if flagb:
            cx20_ = cx20
            flagb = False
        dcx20 = cx20 - cx20_
        cx20_ = cx20

    if results.multi_hand_landmarks:

        #To draw the hand landmarks if needed
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
        
        #Volume Control
        if volumec:
            if cy(12) > cy(9) and cy(16) > cy(13) and cy20 > cy(17) and flag and cy(5) > cy8:
                volume = dcy8
                flag = False
                mute, unmute, brightnessc, cursor = False, False, False, False
            else:
                mute, unmute, brightnessc, cursor = True, True, True, True

            if flag3 == True:
                if volume > 0:
                    #Decreasing volume based on our point finger y coordinate
                    pyautogui.press("volumedown",int(int(volume)/3))
                    flag3 = False
                else:
                    #Increasing volume based on our point finger y coordinate
                    pyautogui.press("volumeup",int((int(volume)*-1)/3))
                    flag3 = False
        
        #Mute
        if mute:
            if cy(12) > cy(9) and cy(16) > cy(13) and cy20 > cy(17) and cy8 > cy(5):
                if mute2 == 1:
                    mute, mute2 = 0, 0
                    volumec, unmute, brightnessc, cursor = False, False, False, False
            else:
                volumec, unmute, brightnessc, cursor = True, True, True, True

            if mute == 0:
                #Muting volume
                pyautogui.hotkey('volumemute')
                mute = 1
        
        #Unmute
        if unmute:
            if cy(12) < cy(9) and cy(16) < cy(13) and cy20 < cy(17) and cy8 < cy(5):
                mute2 = 1
                volumec, mute, brightnessc, cursor = False, False, False, False
            else:
                volumec, mute, brightnessc, cursor = True, True, True, True
            
        #Brightness Control
        if brightnessc:
            if cy(12) > cy(9) and cy(16) > cy(13) and cy20 < cy(17) and flag and cy(5) < cy8:
                brightness = dcx20
                flag, flagb2 = False, True
                volumec, mute, unmute, cursor = False, False, False, False
            else:
                volumec, mute, unmute, cursor = True, True, True, True
                
            if flagb2 == True:
                if brightness > 0:
                    #Increase brightness based on our pinky x coordinate
                    sbc.set_brightness('+'+str(int(brightness/2)))
                    flagb2 = False
                else:
                    #Decreaseing brightness based on our pink x coordinate
                    sbc.set_brightness('-'+str(int(brightness/2)*-1))
                    flagb2 = False
        
        #Cursor Control
        if cursor:
            if cy(12) < cy(9) and cy(16) > cy(13) and cy20 > cy(17) and cy8 < cy(5):
                flagc = True
                volumec, mute, unmute, brightnessc = False, False, False, False
            else:
                volumec, mute, unmute, brightnessc = True, True, True, True

            if flagc:

                #Move cursor according to finger position
                mouse.position = (int(cx(12)*1.8),int(cy(12)*1.8))

                #Left click
                if cy8 > cy(11) and counter == 0:
                    mouse.press(Button.left)
                    counter = 1
                #Right click
                if cy(12) > cy(7) and counter2 == 0:
                    mouse.press(Button.right)
                    counter2 = 1
                #Release left click
                if cy8 < cy(11) and counter == 1:
                    mouse.release(Button.left)
                    counter = 0
                #Release right click
                if cy(12) < cy(7) and counter2 == 1:
                    mouse.release(Button.right)
                    counter2 = 0
                flagc = False
    print(cx(20))           
    #Combining User Guide Manual and Webcam
    Hori = np.concatenate((image,im), axis=1) 

    #Displaying Video
    cv2.imshow(':D', Hori)

    #Close Program by pressing "x" or the close button
    if cv2.waitKey(1) == ord('q'): 
        break
    elif cv2.getWindowProperty(":D",cv2.WND_PROP_VISIBLE) < 1:        
        break 

cap.release()