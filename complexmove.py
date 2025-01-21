from time import sleep
import RPi.GPIO as GPIO

# We name all the pins on BCM mode, use them as their GPIO number and NOT PIN number
GPIO.setmode(GPIO.BCM)

SERVO = 17 # Servo GPIO pin
ENABLE = 27   # ENABLE (pwm/step)
PHASE = 22 # PHASE

CW = GPIO.LOW  # Clockwise Rotation
CCW = GPIO.HIGH    # Counterclockwise Rotation
SPR = 200   # Steps per Revolution as stated on datasheet of the Joy-it Nema 17-03

GPIO.setup(SERVO, GPIO.OUT)
GPIO.setup(ENABLE, GPIO.OUT)
GPIO.setup(PHASE, GPIO.OUT)
GPIO.output(PHASE, CW)

step_count = SPR
stepperDelay = .00003
xstepper=GPIO.PWM(ENABLE, 20000) #20 kHz, datasheet states 0 - 250 kHz
xstepper.start(15) 

servoMovementDeadZone = 1
servoMin = 20
servoMax = 80
currentY = 35
yservo=GPIO.PWM(SERVO, 330) #330hz as per servo datasheet
yservo.start(currentY) #20-80
sleep(0.3)
yservo.ChangeDutyCycle(0)
xstepper.ChangeDutyCycle(0)

def CleanupGPIO():
	yservo.stop()
	GPIO.cleanup()
	
def MoveStepper(myDIR, mySTEPS):
	direction = CCW # input 0 for CCW, 1 for CW
	if(myDIR == 1):
	    direction = CW
	GPIO.output(PHASE, direction)
	
	xstepper.ChangeDutyCycle(15)
	sleep(stepperDelay * mySTEPS) #delay longer with more steps
	
	GPIO.output(ENABLE, GPIO.LOW)
	xstepper.ChangeDutyCycle(0)
	

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
