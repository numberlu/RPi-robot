## libraries to import to rpi:
	sudo apt-get update
	sudo apt-get upgrade

	sudo apt-get install python3-rpi.gpio
 	sudo pip3 install gpiozero
  	sudo apt-get install python-smbus
	sudo apt-get install i2c-tools
 	sudo pip3 install adafruit-circuitpython-servokit
  	sudo apt-get install python3-adafruit-circuitpython-pca9685
  	sudo apt-get install python3-opencv
	sudo apt-get install libqt4-test python3-sip python3-pyqt5 libqtgui4 libjasper-dev libatlas-base-dev -y
	pip3 install opencv-contrib-python==4.1.0.25
	sudo modprobe bcm2835-v4l2


## sources for the code (inspiration):	
- [for Servo manipulation](https://www.digikey.com/en/maker/tutorials/2021/how-to-control-servo-motors-with-a-raspberry-pi)
- [I2C protocol setup](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c)
- [QR scanner](https://www.hackster.io/gatoninja236/scan-qr-codes-in-real-time-with-raspberry-pi-a5268b)
- [Adafruit libraries](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi)
