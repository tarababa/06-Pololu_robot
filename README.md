#Pololu Robot

This application controls a robot based on [Pololu's Zumo Chassis kit](http://www.pololu.com/product/1418). 
It has two [motors](http://www.pololu.com/product/2367) controlled by a [Pololu Qik 2s9v1 Dual Serial Motor Controller](http://www.pololu.com/product/1110)
The application is written to be compatible with Python 3.2.3 and is intended to run on a Raspberry PI.
A simple web application is provided to show a control panel and a video stream from the camera attached to the Raspberry PI.

#Starting the application
------------------------
Start the application in the robot folder using `sudo python3 PololuRobot.py`


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
4. pyserial
 * ```sudo pip-3.2 install pyserial```
 * or ```sudo apt-get install python3-serial```

##[U4VL](http://www.linux-projects.org/modules/sections/index.php?op=viewarticle&artid=14)
We need U4VL to stream the video from the Raspberry Pi camera. The installation instructions can be found on the [U4VL website](http://www.linux-projects.org/modules/sections/index.php?op=viewarticle&artid=14) but are added here for completion's sake (however they may not be up-to-date).

```
curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -
```

Add the following line to the file /etc/apt/sources.list :

```deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ wheezy main```
 
then

```
sudo apt-get update
sudo apt-get install uv4l uv4l-raspicam
sudo apt-get install uv4l-raspicam-extras
sudo apt-get install uv4l-mjpegstream
sudo apt-get install uv4l-server
 ```
to stop and start:
```
sudo service uv4l_raspicam stop|start|restart
```
define width and height for stream
```
uv4l --driver raspicam --auto-video_nr --width 640 --height 480
```

Use the uv4l built in server to watch a video stream from the camera

http://raspberrypi:8080/stream/video.mjpeg
   
##mjpg streamer (deprecated)

``` 
mkdir /home/pi/mjpg-streamer
cd /home/pi/mjpg-streamer

sudo apt-get install libjpeg8-dev
sudo apt-get install imagemagick
sudo apt-get install subversion

svn co https://svn.code.sf.net/p/mjpg-streamer/code/mjpg-streamer/ . 

make clean 
make 


uv4l --driver raspicam --auto-video_nr --width 640 --height 480 
cd mjpg-streamer raspberrypi ~ $ export LD_LIBRARY_PATH="$(pwd)"
LD_PRELOAD=/usr/lib/uv4l/uv4lext/armv6l/libuv4lext.so ./mjpg_streamer -i "input_uvc.so -d /dev/video0 -r 640x480 -f 30" -o "output_http.so -w ./www" 
```

Now you can connect to the server and watch the output from the camera

http://raspberrypi:8080/stream.html 

##Serial Port
As we are going to use the UART port for communication with the motor control it cannot be used as a serial console which is setup by default and must be disabled.
remove any references to `ttyAMA0` from the /boot/cmdline.txt file, in the example below `console=ttyAMA0,115200` and `kgdboc=ttyAMA0,115200`
must be removed.

```dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 dwc_otg.speed=1 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait```

which after editting looks like:

```dwc_otg.lpm_enable=0 dwc_otg.speed=1 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait```

You'll also have to edit the `/etc/inittab` file, search for lines specifying the serial port `ttyAMA0`. 
Use “#” at the start of the line to comment them out.  

For the changes to take effect the the Raspberry Pi must be restarted `sudo shutdown -r now`


##Pololu Robot 
Clone the Pololu Robot project
```git clone https://github.com/tarababa/06-Pololu_robot.git```
To start the applicaton navigate to ./06-Pololu_robot/src/ and run the application
```sudo python3 PololuRobot.py```


