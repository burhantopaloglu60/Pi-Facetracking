from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

# We name all the pins on BCM mode, use them as their GPIO number and NOT PIN number
GPIO.setmode(GPIO.BCM)

SERVO = 17 # Servo GPIO pin
DIR = 22   # Direction GPIO Pin
STEP = 27  # Step GPIO Pin
EN = 14 # Enable GPIO Pin

CW = 0     # Clockwise Rotation
CCW = 1    # Counterclockwise Rotation
SPR = 200   # Steps per Revolution as stated on datasheet of the Joy-it Nema 17-03

GPIO.setup(SERVO, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)
GPIO.output(DIR, CW)
GPIO.output(EN, GPIO.LOW)

step_count = SPR
Fastest = .0001
FAST = .001
MEM = .002
SLOW = .01
CRUISE = .0208
stepperDelay = MEM

servoMovementDeadZone = 1
servoMin = 20
servoMax = 80
currentY = 35
yservo=GPIO.PWM(SERVO, 330) #330hz as per servo datasheet
yservo.start(currentY) #20-80
sleep(0.5)
yservo.ChangeDutyCycle(0)

def CleanupGPIO():
	yservo.stop()
	GPIO.output(EN, GPIO.HIGH)
	GPIO.cleanup()
	
def MoveStepper(myDIR, mySTEPS):
	GPIO.output(DIR, myDIR)
	for x in range(int(mySTEPS)):
                GPIO.output(STEP, GPIO.HIGH)
                sleep(stepperDelay)
                GPIO.output(STEP, GPIO.LOW)
                sleep(stepperDelay)

def ServoSetDutyCycleDirect(dcy):
    yservo.ChangeDutyCycle(dcy)

def MoveServo(dcy):
    global currentY
    moveTo = currentY
    
    # move porportional to screen, range = -(servoMin - 100) * 0.1 to +(servoMin - 100) * 0.1
    moveTo += (dcy - moveTo) * 0.1
    
    #cap movement to 20-80
    if moveTo > servoMax:
        moveTo = servoMax
    elif moveTo < servoMin:
        moveTo = servoMin

    if abs(moveTo - currentY) > servoMovementDeadZone: #move only if there is any measurable difference, dont jitter
        yservo.ChangeDutyCycle(moveTo)
        currentY = moveTo
    else:
        yservo.ChangeDutyCycle(0)
