import time
import cv2
from board import SCL, SDA
import busio
import RPi.GPIO as GPIO
from pyzbar.pyzbar import decode
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

#TODO if most of the picture is black
#TODO: check if sorted correctly with IR sensors
# GPIO setup, set IR sensors as input
GPIO.setmode(GPIO.BCM)
IR_PIN = 17
GPIO.setup(IR_PIN, GPIO.IN)
IR_1 = 27
GPIO.setup(IR_1, GPIO.IN)
IR_2 = 22
GPIO.setup(IR_2, GPIO.IN)
IR_3 = 23
GPIO.setup(IR_3, GPIO.IN)
IR_4 = 24
GPIO.setup(IR_4, GPIO.IN)

cam = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

def stop_first_belt():
    #TODO: stop the motor 
    return

#TODO: we might want to take a few images to be sure it is focused
def take_photo():
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    if ret: 
        return image 
    cam.release()
    return None
    
#decodes the qr code and sends back data
def decode_qr(image):
    decoded_objects = decode(image)
    for obj in decoded_objects:
        return obj.data.decode("utf-8")
    print("No QR codes found")
    return None
    
#TODO: what happens if there are more than one disks    
def move_servo(servo, IR_SENSOR):
    servo.angle = 90 
    while not GPIO.input(IR_SENSOR):
        time.sleep(1)
    servo.angle = 0
    return

def move_first_belt():
    #TODO: start to move belt
    return

def which_servo(data):
    match data:
        case "Vilnius":
            move_servo(SERVO_1, IR_1)
        case "Eindhoven":
            move_servo(SERVO_2, IR_2)
        case "Dublin":
            move_servo(SERVO_3, IR_3)
        case "Sofia":
            move_servo(SERVO_4, IR_4)
        #TODO: if other QR codes just move it down
    return        

def main():
    try:
        while True:
            #TODO: move second belt always
            #check for IR sensor input
            if GPIO.input(IR_PIN):
                stop_first_belt()
                for i in range(5):
                    image = take_photo()
                    if image is not None:
                        data = decode_qr(image)
                        if data is not None:
                            continue
                        else:
                            print("No QR code found")
                    else:
                        print("Failed to take a photo") 
                if data is None:
                    print("Failed to find a QR code: Manual Inspection is needed")
                #TODO: problematic because first one will move just long enough until a second QR is detected     
                move_first_belt()
                which_servo()
                time.sleep(0.3)
    except KeyboardInterrupt:
        print("Program terminated")
    finally:
        GPIO.cleanup()
            

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
    SERVO_3 = servo.Servo(pca.channels[12])
    SERVO_4 = servo.Servo(pca.channels[15])

except Exception as e:
    print(f"An error occurred with initializing servos: {e}")


if __name__ == '__main__':
    main()
#signals from IR make the belt stop and camera take a picture (or 5 for example)
#cv2 decodes images and moves servos

