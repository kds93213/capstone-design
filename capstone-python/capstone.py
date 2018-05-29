import cv2
import sys
import logging as log
import datetime as dt
from time import sleep
import pyrebase
import time

UID = "JVgH7WoDyxbFYUDwtXxsJp9Wv9o1"
NULL = dt.datetime.max
EPOCH = dt.datetime.utcfromtimestamp(0)

def getNow():
    return time.mktime(dt.datetime.now().timetuple())


def checkStudyState():
    cascPath = "haarcascade_frontalface_default.xml"
    eyesPath = "M. Rezaei- Closed Eye Classifier.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)
    eyesCascade = cv2.CascadeClassifier(eyesPath)
    log.basicConfig(filename='webcam.q', level=log.INFO)


    config = {
      "apiKey": "AIzaSyBGRCzoGzO4yLeDbH5K_sXAQHAl06OVC0Q",
      "authDomain": "capstonedesign-d1b76.firebaseapp.com",
      "databaseURL": "https://capstonedesign-d1b76.firebaseio.com/",
      "storageBucket": "capstonedesign-d1b76.appspot.com"
    }
    firebase = pyrebase.initialize_app(config)

    db = firebase.database()
    userinfo = db.child("user-info").child(UID)
    userinfo.child("isSleepy").set(True)
    print "set sleepy"

    isSleepyRef = userinfo.child("isSleepy")


    video_capture = cv2.VideoCapture(0)
    anterior = 0

    i = 0

    suspicious = False
    suspicious_start = NULL
    faceOnScreen = True
    noFace_start = NULL
    restNow = False


    todayTimeStamp = str(dt.datetime.now().date())

    startTime = db.child("study-time").child(UID).child(todayTimeStamp).child("faceStartTime").get().val()
    endTime = db.child("study-time").child(UID).child(todayTimeStamp).child("faceEndTime").get().val()
    totalPausedTime = db.child("study-time").child(UID).child(todayTimeStamp).child("facePausedTime").get().val()
    totalResumeTime = db.child("study-time").child(UID).child(todayTimeStamp).child("faceResumeTime").get().val()

    if not startTime:
        startTime = 0
    else:
        totalResumeTime += startTime
    if not endTime:
        endTime = 0
    else:
        totalPausedTime += endTime

    if not totalPausedTime:
        totalPausedTime = 0
    if not totalResumeTime:
        totalResumeTime = 0

    print "start time : "+str(dt.datetime.fromtimestamp(startTime/1000.0))
    print "end time : "+str(dt.datetime.fromtimestamp(endTime/1000.0))
    print "totalPaused time : "+str(dt.datetime.fromtimestamp(totalPausedTime/1000.0))
    print "totalResume time : "+str(dt.datetime.fromtimestamp(totalResumeTime/1000.0))


    while True:
        # study_started = True
        # start recognition
        while video_capture.isOpened():

            study_started = True
            # if not video_capture.isOpened():

            # Capture frame-by-frame
            ret, frame = video_capture.read()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=7,
                minSize=(30, 30)
            )

            eyes = eyesCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=8,
                minSize=(30, 30)
            )

            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                i += 1

            for (x, y, w, h) in eyes:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                i += 1

            # face with no eyes
            if suspicious and len(faces) and 2 > len(eyes):
                if restNow:
                    print "resumed!"
                    totalResumeTime += getNow()
                    db.child("study-time").child(UID).child(todayTimeStamp).child("faceResumeTime").set(totalResumeTime)
                print "you started to focus on your work!"
                faceOnScreen = True
                noFace_start = NULL
                suspicious = False
                suspicious_start = NULL
                restNow = False
                db.child("user-info").child(UID).child("isSleepy").set(False)
                if not startTime:
                    now = getNow()
                    startTime = now
                    db.child("study-time").child(UID).child(todayTimeStamp).child("faceStartTime").set(now)

            # face with closed eyes
            if not suspicious and 1 < len(eyes):
                suspicious = True
                suspicious_start = dt.datetime.now()

            if not restNow and suspicious:
                print (dt.datetime.now() - suspicious_start).total_seconds()

                # suspicious time over 5 sec
                if (dt.datetime.now() - suspicious_start).total_seconds() > 5:
                    db.child("user-info").child(UID).child("isSleepy").set(True)
                    totalPausedTime += getNow() - 5000
                    db.child("study-time").child(UID).child(todayTimeStamp).child("facePausedTime").set(totalPausedTime)
                    restNow = True
                    print "YOU ARE SLEEPING!!"
                    print "suspicious 5 sec over!"

            # no face on screen
            if not len(faces) and faceOnScreen:
                print "there is no face on screen"
                faceOnScreen = False
                noFace_start = dt.datetime.now()
            elif len(faces):
                faceOnScreen = True
                noFace_start = NULL

            if not restNow and not faceOnScreen and (dt.datetime.now() - noFace_start).total_seconds() > 5:
                db.child("user-info").child(UID).child("isSleepy").set(True)
                totalPausedTime += getNow() - 5000
                db.child("study-time").child(UID).child(todayTimeStamp).child("facePausedTime").set(totalPausedTime)
                restNow = True
                print "ARE YOU TAKING A REST?"
                print "there is no face on camera!!"

            # Display the resulting frame
            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                study_started = False
                break

            # Display the resulting frame
            cv2.imshow('Video', frame)

        if not study_started:
            break
        else :
            print('Unable to load camera.')
            sleep(5)
            pass

    db.child("user-info").child(UID).child("isSleepy").set(True)
    now = getNow()
    db.child("study-time").child(UID).child(todayTimeStamp).child("faceEndTime").set(now)

if __name__ == "__main__":
    checkStudyState()