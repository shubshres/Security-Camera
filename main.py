# import opencv: computer vision detecting package
# pip install opencv-python
# https://pypi.org/project/opencv-python/
import cv2

# importing time so user has time to leave after starting code
import time

# install python audio dependencies in order to play audio output
# pip3 install pyttsx3

# import playsound to play sound of timer
# pip3 install playsound
# https://pypi.org/project/playsound/
from playsound import playsound

# importing OS to get current working directory
import os

# importing text to speech engine
import pyttsx3

# import twilio library to send SMS messages
# pip3 install twilio
# https://www.twilio.com/docs/libraries/python
from twilio.rest import Client

# Twilio Account Information
TWILIO_SID = "YOUR TWILIO SID HERE"
TWILIO_AUTH_TOKEN = "YOUR TWILIO AUTH TOKEN HERE"

# global boolean to detect motion
global motion_detected
motion_detected = False

# global boolean that will determine if the program will run
global run_program
run_program = True


# defining a function called lockdown that will run the camera operations
def run_camera():
    # global boolean that will detect if motion is detected
    global motion_detected

    # global boolean that will determine if the program will run
    global run_program

    # capturing video from camera using the cv2 package
    # passed number 2 since I have two cameras plugged into the computer i tested
    # if running on personal computer try passing in 0
    camera = cv2.VideoCapture(0)

    # running code while the camera is on
    while (camera.isOpened()) and (motion_detected != True):
        # initializing two variables, retrieve and camera
        # We will be using two frames and compare them to see if motion is detected
        # frame 1
        retrieve, frame1 = camera.read()

        # frame 2
        retrieve, frame2 = camera.read()

        # creating a variable called difference to see if there is a difference
        # between the two frames
        raw_motion_detect = cv2.absdiff(frame1, frame2)

        # converting color to gray to reduce error coming from detecting motion using color
        motion_detect_gray = cv2.cvtColor(raw_motion_detect, cv2.COLOR_RGB2GRAY)

        # converting image to a blur image
        # pass in motion detect, kernel size, and sigma x
        motion_detect_blur = cv2.GaussianBlur(motion_detect_gray, (5, 5), 0)

        # creating a threshold to remove noise -- see sharper image
        _, thresh = cv2.threshold(motion_detect_blur, 20, 255, cv2.THRESH_BINARY)

        # dilation -- focusing on the interested things
        dilated_capture = cv2.dilate(thresh, None, iterations=3)

        # find border around items that are moving -- contours
        contour, _ = cv2.findContours(dilated_capture, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # checking to see if a big movement is detected
        for i in contour:
            # ignoring smaller movements
            if cv2.contourArea(i) < 10000:
                continue

            # for every contour, store axis positions, width, and height
            x, y, w, h = cv2.boundingRect(i)

            # draw rectangle on big movements
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # if motion is detected set motion detection to true
            motion_detected = True

            # if motion is detected break out of the loop
            if motion_detected:
                break

        # wait 10 ms and see if the user presses a key to exit
        # if user presses q, exit code
        if cv2.waitKey(10) == ord('q'):
            run_program = False
            break

        # show the camera
        cv2.imshow('Security Camera', frame1)


# wait for 30 seconds for user to go away
# check if timer audio is present
try:
    # getting the countdown sounds path
    timer_audio = os.getcwd()
    timer_audio = timer_audio + "/countdown.mp3"
    # playing the timer audio
    playsound(timer_audio)
except:
    # if timer audio is not present, just sleep for 30 seconds
    # run camera after 30 seconds of enabling
    time.sleep(30)
    # pass without errors
    pass


while run_program:
    # run the camera
    run_camera()

    # if motion is detected text the user
    if motion_detected:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        # creating the message
        message = client.messages.create(
            body="MOTION HAS BEEN DETECTED!",
            from_="YOUR TWILIO PHONE NUMBER HERE",
            to="YOUR PHONE NUMBER HERE"
        )
        
        # resetting motion detected boolean
        motion_detected = False

        # run camera again after 30 seconds of idling and rerun program
        time.sleep(30)
