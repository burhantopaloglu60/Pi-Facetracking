from picamera2 import Picamera2
import time
import cv2
#import torch
from complexmove import MoveStepper, MoveServo, CleanupGPIO, ServoSetDutyCycleDirect
#./complexmove
#PID = D
"""
//dev
how do we pick a target before knowing who is which target?
fixing servo jitter on y axis, currently disabled
"""

resXmax = 640
resYmax = 360 

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (resXmax,resYmax)}))
#camera.framerate(30)
camera.start()

# Load YOLOv5 model
#model = torch.hub.load('ultralytics/yolov5', 'yolov5n')
faceCascade = cv2.CascadeClassifier('/home/burhan/Documents/python_scripts/tired/haarcascade_frontalface_default.xml')

x_AxisDeadZone = resXmax * 0.05
y_AxisDeadZone = resYmax * 0.05

followx = 0
followy = 0

def move(x,y,w,h):
    followx = x + w / 2 #facepos
    followy = y + h / 2 #facepos
    
    #center of screen - center of face
    diffY = resYmax / 2 - followy
    diffX = resXmax/ 2 - followx
    
    isCCW = 1 
    #compare to center of screen to center of face
    if followx > resXmax/2:
      isCCW = 0
    
    #difference in center of face and center of screen
    absDiffX = abs(diffX)
    if absDiffX > x_AxisDeadZone: #set deadzone
        MoveStepper(isCCW, absDiffX)
      
    if abs(diffY) > y_AxisDeadZone: 
        #the face position relative to screen, outputs 0 to 100
        MoveServo(followy / resYmax * 100)
    else:
        ServoSetDutyCycleDirect(0)

while True:
    #ret, frame = cap.read()
    frame = camera.capture_array()
    #ret, buffer = cv2.imencode('.jpg', frame)
    #flip frame
    frame = cv2.flip(frame, -1)
    ret = cv2.imencode('.jpg', frame)
    #frame = buffer.tobytes()
    if not ret:
        break

    # Perform face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,     
        scaleFactor=1.2,
        minNeighbors=5,     
        minSize=(20, 20)
    )

    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        move(x,y,w,h)


    #results = model(frame)

    # Draw bounding boxes
	#for result in results.xyxy[0]:
    #    x1, y1, x2, y2, conf, cls = result
     #   if cls == 0:  # Class 0 is 'person' in COCO dataset
      #      cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
       #     followx = x1
        #    followy = y1

    # Display the resulting frame
    cv2.imshow('Face Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#cap.release()
CleanupGPIO()
cv2.destroyAllWindows()
