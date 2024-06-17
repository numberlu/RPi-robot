import time
import cv2
from board import SCL, SDA
import busio
import RPi.GPIO as GPIO
from pyzbar.pyzbar import decode
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
import serial
from serial.serialutil import *
import sys, getopt

class Communication:
    def __init__(self, port):
        self.ser = None
        self.connected = False
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            # self.ser = serial.Serial()
            # self.ser.port = port
            # self.ser.bardrate = 115200
            # self.ser.timeout = 1
            self.ser.setDTR(True)
            time.sleep(0.5)
            self.ser.setDTR(False)
            # self.ser.open()
        except:
            print("serial open failed")
    
    def setMotor(self, chan, speed):
        self.ser.write(bytes(f"{chan},{speed}\n", encoding='utf8'))
    
    def __del__(self):
        if (self.ser is not None):
            self.ser.close()

def stop_first_belt(comm):
    comm.setMotor(1, 0) 
    return

#Takes photo, returns an image
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
    
#moves servo and waits until something passes by allocated IR sensor    
def move_servo(servo, IR_SENSOR):
    if servo is not None:
        servo.angle = 90 
        while True:
            if GPIO.input(IR_SENSOR):
                break
        servo.angle = 0
    else:
        while True:
            if GPIO.input(IR_SENSOR):
                break
    return

def move_first_belt(comm):
    comm.setMotor(1, 255)
    return


def which_servo_1(data):
    match data:
        case "Amsterdam":
            data = 0
        case "Vilnius":
            data = 1
        case "Eindhoven":
            data = 2
        case "Dubai":
            data = 3
        case _:
            if GPIO.input(IR_SENSORS[5]):       #if the last IR sensor senses it, it returns (beacause no servo is needed)
                return
    move_servo(SERVOS[data], IR_SENSORS[data])
    return
                 
def which_servo_2(data):
    if data == 4:
        if GPIO.input(IR_SENSORS[5]):       #if the last IR sensor senses it, it returns (beacause no servo is needed)
                return
    else:
        move_servo(SERVOS[data], IR_SENSORS[data])
        return

def prompt_choice():
    print("Choose the way to sort:")
    print("Press 1 to sort by QR codes")
    print("Press 2 to sort by queue")
    print("Press anything else to quit")
    return input(">>") 

def main(argv):
    portPath = None
    try:
        opts, args = getopt.getopt(argv,"hp:",["port="])
    except getopt.GetoptError:
        print ("test.py -p <serial_port>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print ("test.py -p <serial_port>")
            sys.exit()
        elif opt in ("-p", "--port"):
            portPath = arg
    if portPath is None:
        print ("\033[91mError: specify port")
        sys.exit(2)

    comm = None
    try:
        if comm is None:
            comm = Communication(portPath)
    except Exception as e:
        print(e)
        del comm
        comm = None

    try:
        choice = prompt_choice()

        #Sorting based on QR codes
        if choice is 1:
            while True:
                #check for IR sensor input
                if GPIO.input(IR_PIN):
                    stop_first_belt(comm)
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
                    move_first_belt(comm)
                    which_servo_1(data)

        #Sorting based on queue
        elif choice is 2:
            while True:
                for i in range(5):
                    #check for IR sensor input on first belt
                    if GPIO.input(IR_PIN):
                        stop_first_belt(comm)   
                        move_first_belt(comm)
                        which_servo_2(i)
                    if i == 4:
                        i = -1

        else:
            print("Quitting...")
            print("Program terminated")
            return
    except KeyboardInterrupt:
        print("Program terminated")
    finally:
        GPIO.cleanup()
            

#the program starts from here by trying to initialise ada and servos
try:
    # GPIO setup, set IR sensors as input
    GPIO.setmode(GPIO.BCM)
    IR_PIN = 17
    GPIO.setup(IR_PIN, GPIO.IN)
    IR_SENSORS = {27, 17, 22, 23, 24, 12}
    for i in range(6):
        GPIO.setup(IR_SENSORS[i], GPIO.IN)

    # Initialize I2C bus
    i2c_bus = busio.I2C(SCL, SDA)

    # Create PCA9685 class instance
    pca = PCA9685(i2c_bus)
    pca.frequency = 50

    #Creating servo objects on PCA channels 0, 7, 12 and 15 
    SERVOS = {}
    SERVOS[0] = servo.Servo(pca.channels[0])
    SERVOS[1] = servo.Servo(pca.channels[7])
    SERVOS[2] = servo.Servo(pca.channels[12])
    SERVOS[3] = servo.Servo(pca.channels[15])


except Exception as e:
    print(f"An error occurred with initializing servos: {e}")


if __name__ == '__main__':
    main(sys.argv[1:])

