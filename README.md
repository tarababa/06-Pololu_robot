#Pololu Robot

This application controls a robot based on [Pololu's Zumo Chassis kit](http://www.pololu.com/product/1418). 
The application is written to be compatible with Python 3.2.3 and is intended to run on a Raspberry PI.
A simple web application is provided to show a control panel and a video stream from the camera attached to the Raspberry PI.
The following chapters describe the software and hardware setup in a bit more detail.



#Setup
-----
Before this application can run some libraries need to be installed and the Raspberry Pi configured.

##Python Libraries
For the web interface to control the robot we need WebOb and wheezy.routing. For the interface between the Raspberry Pi and the motor controller we need pyserial.


1. install pip  (this will also install python3-setuptools)
  * ```sudo apt-get install python3-pip```
2. Now you can install WebOb
  * ```sudo pip-3.2 install WebOb```
3. wheezy.routing
  * ```sudo pip-3.2 install wheezy.routing```
4. pyserial, no longer necessary to manually install as it is available with the current Raspbian images
 * ```sudo pip-3.2 install pyserial```
 * or ```sudo apt-get install python3-serial```

##[U4VL](http://www.linux-projects.org/modules/sections/index.php?op=viewarticle&artid=14)
We need U4VL to stream the video from the Raspberry Pi camera. The installation instructions can be found on the [U4VL website](http://www.linux-projects.org/modules/sections/index.php?op=viewarticle&artid=14) but are added here for completion's sake (however they may not be up-to-date).

```
curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -
```

Add the following line to the file */etc/apt/sources.list* :

```deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ wheezy main```
 
then

```
sudo apt-get update
sudo apt-get install uv4l uv4l-raspicam
sudo apt-get install uv4l-raspicam-extras
sudo apt-get install uv4l-mjpegstream
sudo apt-get install uv4l-server
 ```

Edit the UV4L configureation file */etc/uv4l/uv4l-raspicam.conf* and uncomment the width and height properties so that that they look like below, all other properties are left unchanged.

```
#
# raspicam options
#

encoding = mjpeg
width = 640
height = 480
framerate = 30
```
 
 
then restart uv4l_raspicam using the restart option:
```
sudo service uv4l_raspicam stop|start|restart
```

Use the uv4l built in server to watch a video stream from the camera, where raspberrypi references the IP-address of your Raspberry Pi

http://raspberrypi:8080/stream/video.mjpeg

##Serial Port
As we are going to use the UART port for communication with the motor control it cannot be used as a serial console which is setup by default and must be disabled.
remove any references to `ttyAMA0` from the /boot/cmdline.txt file, in the example below `console=ttyAMA0,115200` and `kgdboc=ttyAMA0,115200`
must be removed.

```dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 dwc_otg.speed=1 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait```

which after editting looks like:

```dwc_otg.lpm_enable=0 dwc_otg.speed=1 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait```

You'll also have to edit the `/etc/inittab` file, search for lines specifying the serial port `ttyAMA0`. 
Use “#” at the start of the line to comment them out.  

Instead of editting these files the same can be accomplished by using the Raspberry Pi's configuration tool:
* ```sudo raspi-config```
* Choose 8: Advanced Options
* Choose A8: Serial
* Would you like a login shell to be accessible over serial ? -> choose <No>

For the changes to take effect the the Raspberry Pi must be restarted `sudo shutdown -r now`


##Pololu Robot 
Clone the Pololu Robot project
* ```cd $HOME```
* ```git clone https://github.com/tarababa/06-Pololu_robot.git```

Make sure the IP-Address for the webserver is configured correctly: edit *$HOME/06-Pololu_robot/src/etc/config.ini* and make sure the values for ```WEBER_SERVER_IP``` and ````MJPG_STREAM_SERVER``` are relevant for your environment. All other properties need not be changed.

```
[PololuQik]
SERIAL_PORT=/dev/ttyAMA0
BAUD_RATE=38400
[PololuRobotWebControl]
WEB_SERVER_IP=10.0.0.101
WEB_SERVER_PORT=8051
MJPG_STREAM_SERVER=http://10.0.0.101:8080/stream/video.mjpeg
[ObstructionSensors]
FRONT=4
```

To start the application
* ```cd  $HOME/06-Pololu_robot/src/robot/```
* ```sudo python3 PololuRobot.py```


#Hardware
The following chapters cover the various hardware components used and how they are connected. Pin numbers in the following chapters relate to the pin numbers on the Raspberry Pi's GPIO header as published on [www.modmypi.com] (http://www.modmypi.com/blog/raspberry-pi-gpio-cheat-sheet)
![gpio-cheat_sheet](http://www.modmypi.com/image/data/rpi-products/gpio/raspberry-pi-gpio-cheat-sheet.jpg)

##[Zumo Chassis Kit (No Motors)](https://www.pololu.com/product/1418)
This kit comes with sprockets and tracks. The body provides space for 4 AA batteries which will power the motors and the motors themsemelves. Putting the chassis and the motors together is fairly straightforward following the instructions provided on [Pololu's website](https://www.pololu.com/docs/pdf/0J54/zumo_chassis.pdf). The only thing which was a bit hard, as it required quite a bit of force, was pushing the wheels onto the motor's axel.

##[100:1 Micro Metal Gearmotor MP](https://www.pololu.com/product/2367)
The two motors are installed when the zumo chassis kit is put together. The electrical connections are covered in the motor controller chapter.

##[Pololu Qik 2s9v1 Dual Serial Motor Controller](https://www.pololu.com/product/1110)
This motorcontroller receives its commands from the Raspberry Pi through the serial interface and controls the two motors of our robot. The manual can be found on [Pololu's website](https://www.pololu.com/docs/pdf/0J25/qik_2s9v1.pdf). Due to space constraints and because there is no need for them the headers for jumpers are not soldered in (demo-mode, CRC and fixed baud-rate). Also due to space consideration the supplied right angled male header strip was used.
#####Electrical
* GND (logic supply ground) connects to pin 14 (GND)
* VCC (logic voltage)  connects to pin pin 17 (3V3)
* RX (qik serial receive) connects to pin 8 (TXD)
* TX (qik serial send) connects to pin 10 (RXD)
* M1 connects to the right-hand motor
* M0 connects to the left-hand motor
* GND (motor supply ground) connects to negative terminal of the batteries in the battery compartment of the Zumo chassis
* VMOT (motor voltage) connects to the positive terminal of the batteries in the battery compartment of the Zumo chassis

##[Sharp GP2Y0D805Z0F Digital Distance Sensor 5cm](https://www.pololu.com/product/1131)
This distance sensor requires a [carrier](https://www.pololu.com/product/1133) which can also be ordered from Pololu.
This sensor is mounted at the front of the robot and used when running in *roving mode*.
#####Electrical
* GND connects to pin 6 (GND)
* VCC connects to pin 1 (3V3)
* OUT connects to pin 7 (GPIO4)
Should a different I/O pin be desired then the correct GPIO pin needs to be configured in $HOME/....

##[Camera Board 360 Gooseneck Mount](http://www.modmypi.com/raspberry-pi/camera/camera-board-360-gooseneck-mount)
Camera mount which allows the position of the camera to be adjusted without too much fuss.

##[QYG-QP6000-BL QYG QP6000 Micro/30-Pin 6000MA 5V/2.1A Power Bank](http://www.comx-computers.co.za/imageDisplay.php?i=85898_0)
To power the Raspberry Pi I used a 6000mAh powerbank. It was purchased in South Africa at www.kalahari.co.za, the latter has since merged with takelot.com, they still sell powerbanks albeit not this one. I'm sure a suitable alternative can be found.

##[WiFi Dongle - Nano USB](http://www.modmypi.com/raspberry-pi/accessories/wifi-dongles/wifi-dongle-nano-usb)
A wifi dongle to allow the robot to roam untethered



