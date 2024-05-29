import time
import cv2
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

cam = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()
detected_object = False

def stop_belt():
    #TODO: stop the motor 
    return

#TODO: we might want to take a few images to be sure it is focused
def take_photo():
    ret, image = cam.read()
    if not ret:
        print("failed to take an image")
        return
    else: 
        return image
    
#decodes the qr code and sends back data
def qr(image):
    data, vertices_array = detector.detectAndDecode(image)
    # if there is a QR code
    if vertices_array is not None:
        return data
    else:
        print("No QR codes found")
        wait_for_disk()
    
def move_servo(servo, delay):
    servo.angle = 90    #TODO: measure irl
    #TODO: change so that it returns after IR sensor detects disk in the actual bucket
    time.sleep(delay)
    servo.angle = 0
    return

def move_belt():
    #TODO: start to move belt
    return

def which_servo(data):
    match data:
        case "Vilnius":
            move_servo(SERVO_1, 2) #TODO measure irl
        case "Eindhoven":
            move_servo(SERVO_2, 4)
        case "Dublin":
            move_servo(SERVO_3, 6)
    return        

#the working function (maybe we could use main instead of this but idk python well enough)
def wait_for_disk():
    while True:
        if detected_object:
            stop_belt()
            image = take_photo()
            qr(image)
            move_belt()
            which_servo()
            wait_for_disk()

#the program starts from here by trying to initialise ada and servos
try:
    # Initialize I2C bus
    i2c_bus = busio.I2C(SCL, SDA)

    # Create PCA9685 class instance
    pca = PCA9685(i2c_bus)
    pca.frequency = 50

    #Creating servo objects on PCA channels 0, 8 and 15    
    SERVO_1 = servo.Servo(pca.channels[0])
    SERVO_2 = servo.Servo(pca.channels[8])
    SERVO_3 = servo.Servo(pca.channels[15])

except Exception as e:
    print(f"An error occurred: {e}")

wait_for_disk()
#signals from IR make the belt stop and camera take a picture (or 5 for example)
#cv2 decodes images and moves servos

