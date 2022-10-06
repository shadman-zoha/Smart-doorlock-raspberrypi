import urllib
import cv2
import numpy as np
import face_recognition
import os
from firebase.firebase import FirebaseApplication
from datetime import datetime
import time
import requests
import json
import mysql.connector
import pyrebase
import RPi.GPIO as GPIO
from time import sleep


# ##
#flamedetectorpin
channel=5
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel,GPIO.IN)

def callback(channel):
    print("Flame Detect")
    URL = ip_address+"/SmartDoorLockApp/token.php"
    # sending get request and saving the response as response object
    r = requests.get(url=URL)
    # extracting data in json format
    data = r.json()
    for cl in data:
        token=cl["token"]
    print(token)

    serverToken = 'AAAAmgvrpTI:APA91bGJQ5b5d9SKaKWN7vFx_72gKKwBGLTwDRzkKOpm1trMduzPtpvd_9QPKifl1XNnFzfaiN5mrLwf0KbapVigEP3a-hkMVT7jpljZCSvhw-RkcbbzW3XzbclSu1ZNhJNDS0GoJSds'
    deviceToken = token

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
    }

    body = {
        'notification': {'title': 'Fire Alert',
                         'body': 'Your house is on fire, the door is open now for fire!!'
                         },
        'to':
            deviceToken,
        'priority': 'high',
        #   'data': dataPayLoad,
    }
    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers,
                             data=json.dumps(body))
    print(response.status_code)

    print(response.json())
    #db.close()
    firebase = FirebaseApplication('https://smart-door-lock-3f949-default-rtdb.firebaseio.com/', None)
    result = firebase.put('/DHT11/Device1/LED_STATUS/', 'DATA', 'TRUE')
    print(result)
    # end the realtime database update here
    # opening the door if face recognize
    doorUnlock = True
    
    #time.sleep(20)
    # notification code end here
    print('Send alarm')
    

        
   

GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)

# if True:
#     time.sleep(1)
#end here
#end here flame detector


#falme detection new end here

#for light on/off
##pin set
#change ledpin 19 to 24 and add the setwarning line nothing else
ledPin=24
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

##set pin input output
GPIO.setup(ledPin,GPIO.OUT)
#end here light




ip_address="http://www.zoha.live"

doorUnlock = False

#if the door on or off from the app then the value update here
config = {
  "apiKey": "AAAAmgvrpTI:APA91bGJQ5b5d9SKaKWN7vFx_72gKKwBGLTwDRzkKOpm1trMduzPtpvd_9QPKifl1XNnFzfaiN5mrLwf0KbapVigEP3a-hkMVT7jpljZCSvhw-RkcbbzW3XzbclSu1ZNhJNDS0GoJSds",
  "authDomain": "smart-door-lock-3f949.firebaseapp.com",
  "databaseURL": "https://smart-door-lock-3f949-default-rtdb.firebaseio.com/",
  "storageBucket": "smart-door-lock-3f949.appspot.com"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()


def stream_handler(message):

    # print(message["event"]) # put
    # print(message["path"]) # /-K7yGTTEp7O549EzTYtI
    print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
    doorlock= message["data"]
    if doorlock == "TRUE":
        print("Door Open")
        GPIO.output(ledPin, GPIO.HIGH)
        print(GPIO.HIGH)

    else:
        print("Door Lock")
        GPIO.output(ledPin, GPIO.LOW)
        print(GPIO.LOW)



my_stream = db.child("/DHT11/Device1/LED_STATUS/DATA/").stream(stream_handler)


#end here

#encode all saved image from laptop/server
# path = 'assets'
# images = []
# className = []
# myList = os.listdir(path)
# print(myList)
#newcode

URL = ip_address+"/SmartDoorLockApp/imageReadraspberrypi.php"
# sending get request and saving the response as response object
r = requests.get(url=URL)
# extracting data in json format
data = r.json()
print(data)
images = []
className = []

#this function is for load all the image from the assets file
# for cl in myList:
#     curImg = cv2.imread(f'{path}/{cl}')
#     images.append(curImg)
#     className.append(os.path.splitext(cl)[0])
# print(className)
for cl in data:
    req = urllib.request.urlopen(f'{ip_address+"/SmartDoorLockApp/uploads"}/{cl["photos"]}')
    img_array = np.array(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, -1)
    images.append(img)
    className.append(os.path.splitext(cl['names'])[0])
print(className)




#this function is for the encode all the images from the assets file
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
#new code
#def findEncodings(images):
#     encodelist=[]
#     for img in images:
#         img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
#         encode=face_recognition.face_encodings(img)
#         if len(encode) > 0:
#             encodelist.append(encode[0])
#         return encodelist
#end


#this function is for the store attendence
# def markAttendance(name):
#     with open('Attendence.csv','r+') as f:
#         myDataList = f.readlines()
#         nameList = []
#         for line in myDataList:
#             entry = line.split(',')
#             nameList.append(entry[0])
#         if name not in nameList:
#             now = datetime.now()
#             dtString = now.strftime('%H:%M:%S')
#             f.writelines(f'\n{name},{dtString}')


encodeListKnown = findEncodings(images)
print('Encoding Completed')


cap = cv2.VideoCapture(0)
prevTime = time.time()
known = False
unknown = False


##

#this function is for open the webcam then read the image then encode it and compare the image to the known faces and show the result
while True:
    success, img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)
    print(prevTime)
    if time.time() - prevTime > 5:
        prevTime = time.time()
        reading = False
        for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
            print('reading')
            reading = True
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = className[matchIndex].upper()
                # print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                if known == True:
                    # update firebase realtime database for opening the door value= true
                    firebase = FirebaseApplication('https://smart-door-lock-3f949-default-rtdb.firebaseio.com/', None)
                    result = firebase.put('/DHT11/Device1/LED_STATUS/', 'DATA', 'TRUE')
                    print(result)
                    # end the realtime database update here
                    # opening the door if face recognize
                    doorUnlock = True
                    startDoorOpenTime = time.time()
                    # markAttendance(name)
                    print('open the door')
                    GPIO.output(ledPin, GPIO.HIGH)
                    print(GPIO.HIGH)
                    known = False
                else:
                    known = True
                unknown = False


            else:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, 'Unknown', (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                if unknown == True:
                    # capture the picture of unknown faces
                    # # cam = cv2.VideoCapture(0)
                    # image = cap.read()[1]
                    # # cv2.imshow("image", image)
                    # # cv2.imwrite('uploads/unkownFace{}.jpg'.format(int(time.time())), image)
                    # image_path = 'unkownFace{}.jpg'.format(int(time.time()))
                    # path = os.path.join(r'C:\xampp\htdocs\SmartDoorLockApp\unknownfaces/', image_path)
                    # cv2.imwrite(path, image)
                    # date = time.ctime()
                    # # save the unknown face on database
                    # db = mysql.connector.connect(user="root", password="", host="localhost", database="smartdoorlock")
                    # sql = 'INSERT INTO unknownfaces(unknownfaces,timee) VALUES(%s,%s)'
                    # args = (image_path, date,)
                    # mycursor = db.cursor()
                    #
                    # mycursor.execute(sql, args)
                    # db.commit()
                    # db.close()
                    image = cap.read()[1]
                    # cv2.imshow("image", image)
                    # image_path='test1{}.jpg'.format(int(time.time()))
                    image_path = 'unknownImage.jpg'
                    # path=os.path.join('asstes/', image_path)
                    path = os.path.join(r'/home/pi/smartDoorLock_unknownFaces', image_path)

                    cv2.imwrite(path, image)
                    print(image_path)
                    print(type(image))
                    #
                    url = ip_address+"/SmartDoorLockApp/pythonImagesvaer.php"
                    files = {'file': open(r'/home/pi/smartDoorLock_unknownFaces/unknownImage.jpg', 'rb')}

                    r = requests.post(url, files=files)
                    print(url)
                    #
                    # database end here

                    # end here

                    # if the face is unknown then send notification to app
                    #db = mysql.connector.connect(user="zohalive_smartdoorlock", password="Root800@", host="192.168.0.100", database="zohalive_smartdoorlock")
                    #mycursor = db.cursor()
                    #db.commit()

                    #sql = 'select token from token where id=1'
                    #mycursor.execute(sql)
                    #data = mycursor.fetchone()
                    #token = data[0]
                    #print(token)
                    URL = ip_address+"/SmartDoorLockApp/token.php"
                    # sending get request and saving the response as response object
                    r = requests.get(url=URL)
                    # extracting data in json format
                    data = r.json()
                    for cl in data:
                        token=cl["token"]
                    print(token)

                    serverToken = 'AAAAmgvrpTI:APA91bGJQ5b5d9SKaKWN7vFx_72gKKwBGLTwDRzkKOpm1trMduzPtpvd_9QPKifl1XNnFzfaiN5mrLwf0KbapVigEP3a-hkMVT7jpljZCSvhw-RkcbbzW3XzbclSu1ZNhJNDS0GoJSds'
                    deviceToken = token

                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': 'key=' + serverToken,
                    }

                    body = {
                        'notification': {'title': 'Unknown Person Alert',
                                         'body': 'Their is a unknown person in front of your door. Please check!!'
                                         },
                        'to':
                            deviceToken,
                        'priority': 'high',
                        #   'data': dataPayLoad,
                    }
                    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers,
                                             data=json.dumps(body))
                    print(response.status_code)

                    print(response.json())
                    #db.close()
                    
                    time.sleep(20)
                    # notification code end here
                    print('Send alarm')
                    unknown = False
                else:
                    unknown = True
                known = False

        if reading == False:
            known= False
            unknown= False
        






    #lock the door after few seconds
    if doorUnlock == True and time.time() - startDoorOpenTime >10:
        doorUnlock = False
        firebase = FirebaseApplication('https://smart-door-lock-3f949-default-rtdb.firebaseio.com/', None)
        result = firebase.put('/DHT11/Device1/LED_STATUS/', 'DATA', 'FALSE')
        print(result)
        print("Door Lock")
        GPIO.output(ledPin, GPIO.LOW)
        print(GPIO.LOW)
    

    cv2.imshow('Webcam',img)
    cv2.waitKey(1)
    
    










