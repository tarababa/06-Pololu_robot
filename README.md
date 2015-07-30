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
We will be using U4VL to stream the video from the Raspberry Pi camera. The installation instructions can be found on the [U4VL website](http://www.linux-projects.org/modules/sections/index.php?op=viewarticle&artid=14) but are added here for completion's sake (however they may not be up-to-date).

```curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -```

Add the following line to the file /etc/apt/sources.list :

    deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ wheezy main


