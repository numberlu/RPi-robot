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
            self.ser.setDTR(True)
            time.sleep(0.5)
            self.ser.setDTR(False)
        except:
            print("serial open failed")
    
    def setMotor(self, chan, speed):
        self.ser.write(bytes(f"{chan},{speed}\n", encoding='utf8'))
    
    def __del__(self):
        if (self.ser is not None):
            self.ser.close()

#moves servo and waits until something passes by allocated IR sensor    
def move_servo(servo, comm, delay):
    comm.setMotor(2, 255)
    if servo is not None:
        servo.angle = 20
        time.sleep(delay + 1)
        servo.angle = 90
    else:
        time.sleep(delay + 1)
    return

def stop_first_belt(comm):
    comm.setMotor(2, 0) 
    return

def stop_second_belt(comm):
    comm.setMotor(1, 0) 
    return

def move_short_belt(comm):
    comm.setMotor(1, 100)
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
    print("Decoding...")
    decoded_objects = decode(image)
    for obj in decoded_objects:
        return obj.data.decode("utf-8")
    print("No QR codes found")
    return None
    
#moves servo and waits until something passes by allocated IR sensor    
# def move_servo_old(servo, IR_SENSOR):
#     if servo is not None:
#         servo.angle = 20 
#         while True:
#             if GPIO.input(IR_SENSOR):
#                 break
#         servo.angle = 90
#     else:
#         while True:
#             if GPIO.input(IR_SENSOR):
#                 break
#     return

def which_servo(data):
    match data:
        case "Amsterdam":
            index = 0
        case "Vilnius":
            index = 1
        case "Eindhoven":
            index = 2
        case "Dubai":
            index = 3
        case _:
            index = 4
    return index 

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

    #the program starts from here by trying to initialise ada and servos
    # try:
    #     # GPIO setup, set IR sensors as input
    #     GPIO.setmode(GPIO.BCM)
    #     IR_PIN = 17
    #     GPIO.setup(IR_PIN, GPIO.IN)
    #     IR_SENSORS = {27, 17, 22, 23, 24, 12}
    #     for i in range(6):
    #         GPIO.setup(IR_SENSORS[i], GPIO.IN)
    # except Exception as e:
    #     print(f"An error occurred with initializing IR sensors: {e}")

    # Initialize I2C bus
    i2c_bus = busio.I2C(SCL, SDA)

    # Create PCA9685 class instance
    pca = PCA9685(i2c_bus)
    pca.frequency = 50

    try:
        #Creating servo objects on PCA channels 0, 7, 8 and 15 
        SERVOS = {}
        SERVOS[0] = servo.Servo(pca.channels[0])
        SERVOS[1] = servo.Servo(pca.channels[7])
        SERVOS[2] = servo.Servo(pca.channels[8])
        SERVOS[3] = servo.Servo(pca.channels[15])
        SERVOS[4] = None
    except Exception as e:
        print(f"An error occurred with initializing servos: {e}")

    for i in range(4):
        SERVOS[i].angle = 90

    try:
        print("Choose the way to sort:")
        print("Press 1 to sort by QR codes")
        print("Press 2 to sort by queue")
        print("Press 3 to MANUALLY sort by QR codes")
        print("Press 4 to MANUALLY sort disks")
        print("Press anything else to quit")
        choice = input(">> ")

        # # initialize
        # comm.setMotor(1, 255)
        # comm.setMotor(2, 255)
        # time.sleep(1)
        # comm.setMotor(1, 0)
        # comm.setMotor(2, 0)
        # time.sleep(1)

        comm.setMotor(1, 0)
        comm.setMotor(2, 255)

        #Sorting based on QR codes
        if choice == "1":
            while True:
                IR_PIN = False
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
                    else:
                        index = which_servo(data)
                        move_servo(SERVOS[index], comm, index)
                    move_short_belt(comm)

        #Sorting based on queue
        elif choice == "2":
            for i in range(5):
                #check for IR sensor input on first belt
                if GPIO.input(IR_PIN):
                    move_servo(SERVOS[i], comm, i)
                move_short_belt(comm)
                if i == 4:
                    i = -1

        #Sorting based on QR codes
        elif choice == "3":
            while True:
                #check for IR sensor input
                if input("Press x to manually notice a disk: ") == "x":
                    stop_second_belt(comm)
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
                    else:
                        index = which_servo(data)
                        move_servo(SERVOS[index], comm, index)
                    move_short_belt(comm)

        #Sorting based on queue
        elif choice == "4":
            while True:
                if input("Press x to manually notice a disk: ") == "x":
                    choice = input("Choose the servos 1 through 4, where all other inputs are unknown: ")
                    match choice:
                        case "1":      
                            comm.setMotor(1, 100)
                            time.sleep(0.7)
                            comm.setMotor(1, 0)                      
                            move_servo(SERVOS[0], comm, 0)
                        case "2":
                            comm.setMotor(1, 100)
                            time.sleep(0.7)
                            comm.setMotor(1, 0)
                            move_servo(SERVOS[1], comm, 1)
                        case "3":
                            comm.setMotor(1, 100)
                            time.sleep(0.7)
                            comm.setMotor(1, 0)
                            move_servo(SERVOS[2], comm, 2)
                        case "4":
                            comm.setMotor(1, 100)
                            time.sleep(0.7)
                            comm.setMotor(1, 0)
                            move_servo(SERVOS[3], comm, 3)
                        case _:
                            comm.setMotor(1, 100)
                            time.sleep(0.7)
                            comm.setMotor(1, 0)
                            move_servo(SERVOS[4], comm, 4)   
                    comm.setMotor(2, 255)
        else:
            print("Quitting...")
            print("Program terminated")
            return
    except KeyboardInterrupt:
        print("Program terminated")
        comm.setMotor(1, 0)
        comm.setMotor(2, 0)
    finally:
        stop_first_belt(comm)
        stop_second_belt(comm)
        GPIO.cleanup()

if __name__ == '__main__':
    main(sys.argv[1:])

