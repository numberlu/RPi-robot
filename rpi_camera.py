#import RPi.GPIO as GPIO
from gpiozero import Servo
from time import sleep
import cv2

# TODO: implement queue (first belt stopping)
# TODO: implement wait time based on IRL measurements and two belts
wait = 2
 

# GPIO17 - servo #1
servo_1 = Servo(17)
# GPIO27 - servo #2
servo_2 = Servo(27)
# GPIO22 - servo #3
servo_3 = Servo(22)
# GPIO5 - servo #4
servo_4 = Servo(5)

# just placeholders (ba dum tss)
def servo_picker(data):
    match data:
        case "Eindhoven":
            servo_manipulator(servo_1)
        case "Vilnius":
            servo_manipulator(servo_2)
        case "Madrid":
            servo_manipulator(servo_3)
        case "Dubai":
            servo_manipulator(servo_4)


def servo_manipulator(servo):
    try: 
        servo.max()
        sleep(wait)
        servo.min()
    except KeyboardInterrupt:
        print()

# set up camera object
cap = cv2.VideoCapture(0)

# QR code detection object
detector = cv2.QRCodeDetector()

# TODO: figure out how to manipulate camera - how to turn it on/off
while True:
    # get the image
    _, img = cap.read()
    # get bounding box coords and data
    data, bbox, _ = detector.detectAndDecode(img)
    
    # if there is a bounding box, draw one, along with the data
    if(bbox is not None):
        for i in range(len(bbox)):
            cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,
                     0, 255), thickness=2)
        cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
        
        if data:
            print("data found: ", data)
    # display the image preview on the monitor (for now)
    # delete later
    cv2.imshow("code detector", img)
    if(cv2.waitKey(1) == ord("q")):
        break

    servo_picker(data)

# free camera object and exit
cap.release()
cv2.destroyAllWindows()

