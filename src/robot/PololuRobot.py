#    Copyright 2014 Helios Taraba 
#
#    This file is part of PololuRobot.
#
#    PololuRobot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PololuRobot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PololuRobot.  If not, see <http://www.gnu.org/licenses/>.


"""
This module defines the PololuRobot application. The main class in the module is
PololuRobot. It is responsible for insanciating objects of the PololuQik motor 
controller class and the ObstructionSensor class. 
It also is responsible for starting the PololuRobotWebControlApp using the 
WSGI reference implation included in Python.

"""

import sys,os
import time
import logging, traceback
import random
import threading
from wsgiref.simple_server import make_server
sys.path.append(os.path.join('..','motor control'))
sys.path.append(os.path.join('..','web control'))
sys.path.append(os.path.join('..','configuration'))
import PololuQik, Configuration, ObstructionSensor, PololuRobotWebControl    

#tuple defining "radius" of a curve by specifying the percentage of the
#speed of the inner and the outer track (e.g. when turning left the left 
#track is the inner track and should turn slower than the outer track
#to accomplish a left turn)
DFLT_RADIUS=(0.4,1.0)
    
class PololuRobot():
  def __init__(self):
    self.timer=None
    #load configuration
    self.kwargs=self.loadConfig()
    self.logger=self.setupLogging()
    #there is one obstruction sensor at the front of the robot
    self.sensorFront=ObstructionSensor.ObstructionSensor(**self.kwargs)
    #we have one motor controller for both motors
    self.motorControl=PololuQik.PololuQik(**self.kwargs)
    #initialize initial speed
    self.setDriveSpeed=30
    #initially the robot is stopped
    self.stopped=True
    #roving mode can be chosen from web application
    self.isRoving=False
    #evading action (whilst roving)
    self.isEvading=False
    #not driving forwards or backwards to now
    self.drivingForwards=False
    self.drivingBackwards=False
  #------------------------------------------------------------------------------#
  # loadConfig: loads configuration from config.ini and return values as         #
  #             keyword arguments                                                #
  # returnvalues: kwargs                                                         #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#   
  def loadConfig(self):
    ########################
    #GENERAL CONFIGURATION #
    ########################
    #load config
    config=Configuration.general_configuration();
    #get all parameters from config.ini file
    obstructionSensorFront = Configuration.CONFIG['ObstructionSensors']['FRONT']  
    webServerIp            = Configuration.CONFIG['PololuRobotWebControl']['WEB_SERVER_IP']
    webServerPort          = Configuration.CONFIG['PololuRobotWebControl']['WEB_SERVER_PORT']  
    mjpgStreamServer       = Configuration.CONFIG['PololuRobotWebControl']['MJPG_STREAM_SERVER'] 
    serialPort             = Configuration.CONFIG['PololuQik']['SERIAL_PORT']    
    baudRate               = Configuration.CONFIG['PololuQik']['BAUD_RATE']    
    
    kwargs=dict(obstructionSensorFront=obstructionSensorFront, 
                webServerIp=webServerIp, 
                webServerPort=webServerPort,
                mjpgStreamServer=mjpgStreamServer,
                serialPort=serialPort,
                baudRate=baudRate)
    return kwargs
  #------------------------------------------------------------------------------#
  # setupLogging: loads configuration from log.ini, setups a logger and adds it  #
  #               to the dictionary of keyword arguments                         #
  # returnvalues: logger                                                         #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#   
  def setupLogging(self):
    ###############
    #SETUP LOGGING#
    ###############
    LOGGER = 'PololuRobot'
    #load logging configuration
    Configuration.logging_configuration();
    #configure logger as per configuration
    Configuration.init_log(LOGGER);
    #create logger
    logger =  logging.getLogger(LOGGER)
    #add the logger to dictionary of keyword arguments
    self.kwargs.update(logger=logger)
    return logger

  #------------------------------------------------------------------------------#
  # driveBackwards: Make robot drive backwards                                   #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#    
  def driveBackwards(self):
    self.logger.debug('driving backwards')
    #cancel any callback to stop, if it exists
    self.cancelCallback()      
    self.motorControl.setSpeed(-1*self.setDriveSpeed)
    #robot is not stopped
    self.stopped=False
    self.drivingBackwards=True
    
  #------------------------------------------------------------------------------#
  # driveForwards: Make robot drive forwards                                     #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#  
  def driveForwards(self):
    self.logger.debug('driving forwards')
    #cancel any callback to stop, if it exists
    self.cancelCallback()      
    self.motorControl.setSpeed(self.setDriveSpeed)
    #robot is not stopped
    self.stopped=False
    self.drivingForwards=True

  #------------------------------------------------------------------------------#
  # setSpeed: change speed of robot                                              #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#     
  def setSpeed(self, speed):
    self.logger.debug('setting speed')
    #update the speed
    self.setDriveSpeed=speed
    #if driving forwards or backwards we change  
    #the speed the motors are running at
    if self.drivingForwards:
      self.driveForwards()
    elif self.drivingBackwards:
      self.driveBackwards()
    
  #------------------------------------------------------------------------------#
  # stop: stop the robot                                                         #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#     
  def stop(self):
    self.logger.debug('stopping')
    #not driving bakcwards or forwards
    self.drivingForwards=False
    self.drivingBackwards=False  
    #cancel any callback to stop, if it exists
    self.cancelCallback()    
    #set speed to zero, then coast
    self.motorControl.setSpeed(0)      
    self.motorControl.setCoast()
    #robot is stoped
    self.stopped=True
    
  #------------------------------------------------------------------------------#
  # turnRight: turn right. If a value for time is passed the right turn will be  #
  #                        terminated after that time                            #
  #                                                                              #
  # paramteres: time: desired duration in seconds of the right turn.             #
  #                   when time <= 0 then the right turn will carry              #
  #                   on indefinetely                                            #
  #             radius: tuple defining relative speed for inner and outer track  #
  #                     for a right turn the right track is the inner track      #
  #                     and should run slower than the left (outer) track in     #
  #                     order to accomplish a right turn                         #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#      
  def turnRight(self,time=0,radius=DFLT_RADIUS):
    self.logger.debug('turning right')
    #not driving bakcwards or forwards
    self.drivingForwards=False
    self.drivingBackwards=False    
    #cancel any callback to stop, if it exists
    self.cancelCallback()
    #M0 drives the right hand side track i.e. inner side of curve
    #M1 drives the left hand side track i.e. outer side of curve
    #to turn right the left hand side track must turn
    #faster then the right hand side track
    inner_rate,outer_rate = radius
    min_speed = 15
    if int(self.setDriveSpeed * inner_rate) < min_speed:
      M0Speed=min_speed
    else:
      M0Speed=int(self.setDriveSpeed * inner_rate)
    M1Speed= int((M0Speed / inner_rate) * outer_rate)
    self.motorControl.setM0Speed(M0Speed)          
    self.motorControl.setM1Speed(M1Speed)
    self.stopped=False
    #if time has been set > 0 than the right turn 
    #is stopped after that amount of time
    self.callback(function=self.callbackStop, time=time)

  #------------------------------------------------------------------------------#
  # turnLeft: turn left. If a value for time is passed the left turn will be     #
  #                        terminated after that time                            #
  #                                                                              #
  # paramteres: time: desired duration in seconds of the left turn.              #
  #                   when time <= 0 then the left turn will carry               #
  #                   on indefinetely                                            #
  #             radius: tuple defining relative speed for inner and outer track  #
  #                     for a left turn the left track is the inner track        #
  #                     and should run slower than the right (outer) track in    #
  #                     order to accomplish a left turn                          #  
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------# 
  def turnLeft(self,time=0, radius=DFLT_RADIUS):
    self.logger.debug('turning left')
    #not driving bakcwards or forwards
    self.drivingForwards=False
    self.drivingBackwards=False      
    #cancel any callback to stop, if it exists
    self.cancelCallback()
    #M0 drives the right hand side track i.e. outer side of curve
    #M1 drives the left hand side track i.e. inner side of curve
    #to turn left the right hand side track must turn
    #faster then the left hand side track
    inner_rate,outer_rate=radius
    min_speed = 15
    if int(self.setDriveSpeed * inner_rate) < min_speed:
      M1Speed=min_speed
    else:
      M1Speed=int(self.setDriveSpeed * inner_rate)
    M0Speed= int((M1Speed / inner_rate) * outer_rate)
    self.motorControl.setM0Speed(M0Speed)          
    self.motorControl.setM1Speed(M1Speed)
    self.stopped=False
    #if time has been set > 0 than the left turn 
    #is stopped after that amount of time
    self.callback(function=self.callbackStop, time=time)

  #------------------------------------------------------------------------------#
  # callbackStop: This function is called once the callback timer expires which  #
  #               indicates the motors should be stopped. This function is used  #
  #               to terminate turns after a certain amount of time and to       #
  #               reverse away from an obstacle for a certain amount of time when#
  #               in roving mode.                                                #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------# 
  def callbackStop(self):
    self.stop()
  #------------------------------------------------------------------------------#
  # callback: This function starts a timer after which the function passed as a  #
  #            parameter is called. This is used to terminate  turns after a     #
  #            certain amount of time                                            #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#     
  def callback(self,function,time):
    if time > 0:
      self.timer = threading.Timer(time,function)
      self.timer.start()
      self.timer.join()
  #------------------------------------------------------------------------------#
  # cancelCallback: This function is used to terminate a started callback timer. #
  #                 In particular if a turn was stopped by turning the other way #
  #                 driving forwards or backwards or stopping otherwise, any     #
  #                 started callback is no longer required and must therefore be #
  #                 cancelled                                                    #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#           
  def cancelCallback(self):
    try:
      self.timer.cancel()
    except (AttributeError, TypeError):
      #no timer has been started, well that is ok
      None
    except:
      self.logger.warning('failed to cancel timer['+  str(traceback.format_exc()) +']')   
  #------------------------------------------------------------------------------#
  # evade: Evade an obstacle by reversing a bit then turning left or right       #
  #                                                                              #
  #                                                                              #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#           
  def evade(self):
    SHARP_TURN_RADIUS=(-0.6,0.6)
    self.isEvading=True
    action='reverse'
    while self.isEvading and self.isRoving:
      if action=='reverse':
        self.logger.debug('action['+action+']')
        #evasive action starts with reversing
        #until the front sensor no longer sees
        #the obstacle
        self.driveBackwards()
        #we'll drive backwards for one second
        self.callback(function=self.callbackStop, time=1)        
        action='reversing'
      elif action=='reversing':
        self.logger.debug('action['+action+']')
        #waiting for reverse movement to stop
        if self.stopped:
          action='clearedObstacle'
      elif action=='clearedObstacle':
        self.logger.debug('action['+action+']')
        #we are done driving backwards lets
        #see if the sensor still detects 
        #the obstruction
        if not self.sensorFront.obstructed:
          #no obstruction detected
          #lets turn
          action='turn'
        else:
          #oh oh still detecting obstruction
          #lets reverse a bit more
          action='reverse'
      elif action=='turn':
        self.logger.debug('action['+action+']')
        #lets make this exciting and decide
        #randomly whether to turn left or right
        direction=['left','right']
        if random.choice(direction)=='left':
          self.turnLeft(1,SHARP_TURN_RADIUS)
        else:
          self.turnRight(1,SHARP_TURN_RADIUS)
        action='turning'
      elif action == 'turning':
        if self.stopped:
          #turn has been executed, evasive
          #action is complete we can go
          #back to driving around at will
          self.isEvading=False
    
  #------------------------------------------------------------------------------#
  # stopRoving: Terminate roving mode                                            #
  #                                                                              #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#           
  def stopRoving(self):
    self.isRoving=False
    self.stop()
    
  #------------------------------------------------------------------------------#
  # roving: Drive around and avoid collisions                                    #
  #                                                                              #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#           
  def roving(self):
    #initialize evading as it may not
    #not have been set to false if roving
    #was terminated whilst evading
    self.isEvading=False
    #if we had not previously stopped driving we do it now
    self.stop()
    while self.isRoving:
      # if we are not stopped, the front sensor is not detecting an
      # obstruction and we are not in the processes of taking evasive
      # action then we can start driving forwards
      if self.stopped and not self.sensorFront.obstructed and not self.isEvading:
        self.driveForwards()
      # we detected an obstacle, and we are not already taking
      # evasive action than we should go and try to evade the
      # obstacle
      if self.sensorFront.obstructed and not self.isEvading:
        self.evade() # avoid collision
    self.logger.info('leaving roving')

  #------------------------------------------------------------------------------#
  # roving: Start roving in a thread                                             #
  #                                                                              #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#           
  def runRoving(self):
    if not self.isRoving:
      self.isRoving=True
      threadRoving = threading.Thread(target=self.roving)
      threadRoving.name='ROVING'
      threadRoving.start()
        
        
  def __call__(self):
    try:
      return self.main() or 0
    except Exception as e:
      logging.error(str(e))
      return 1    
  #------------------------------------------------------------------------------#
  # main: start the web control server and pass it the pololu robot object       #
  #                                                                              #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#        
  def main(self):
      
    try:
      kwargs=self.kwargs
      #add robot object to kwargs
      kwargs.update(robot=self)
      app = PololuRobotWebControl.PololuRobotWebControlApp(**kwargs)
      #start
      httpd = make_server(str(self.kwargs.get('webServerIp')),int(self.kwargs.get('webServerPort')), app)
      self.logger.debug('webServerIp['+str(self.kwargs.get('webServerIp'))+'] webServerPort['+ str(self.kwargs.get('webServerPort')) +']')
      httpd.serve_forever()
    except (KeyboardInterrupt):
      None
    finally:
      try:
        self.stop()
      except Exception as e:
        logging.error(str(traceback.format_exc()))
      try:
        self.sensorFront.cleanUp()
      except Exception as e:
        logging.error(str(traceback.format_exc()))
    return 0     

main=PololuRobot() 

if __name__ == '__main__':
    sys.exit(main())
