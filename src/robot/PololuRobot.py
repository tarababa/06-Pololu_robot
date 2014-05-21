# ##############################################################################
# Application         : Pololu Robot 
# Created by          : hta
# Created             : hta
# Changed by          : $Author: b7tarah $
# File changed        : $Date: 2013-08-21 15:19:43 +0200 (Mi, 21 Aug 2013) $
# Environment         : Python 3.3.4
# ##############################################################################
# Description : A simple class representing a pololu robot   
#              
################################################################################

import sys,os
import time
import logging, traceback
import random
from threading import Timer
sys.path.append(os.path.join('..','motor control'))
sys.path.append(os.path.join('..','configuration'))
import PololuQik, Configuration, ObstructionSensor    
    
class PololuRobot():
  def __init__(self):
    self.timer=None
    #load configuration
    self.kwargs=loadConfig()
    self.logger=setupLogging()
    #there is one obstruction sensor at the front of the robot
    self.sensorFront=ObstructionSensor.ObstructionSensor(**kwargs)
    #we have one motor controller for both motors
    self.motorControl=PololuQik.PololuQik(**kwargs)
    #initialize initial speed
    self.setDriveSpeed=30
    #initially the robot is stopped
    self.stopped=True
    #evading action
    self.evading=False

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
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#      
  def turnRight(self,time=0):
    self.logger.debug('turning right')
    #cancel any callback to stop, if it exists
    self.cancelCallback()
    #M0 drives the right hand side track i.e. inner side of curve
    #M1 drives the left hand side track i.e. outer side of curve
    #to turn right the left hand side track must turn
    #faster then the right hand side track
    inner_rate=0.5
    outer_rate=0.7
    min_speed = 30
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
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------# 
  def turnLeft(self,time=0):
    self.logger.debug('turning left')
    #cancel any callback to stop, if it exists
    self.cancelCallback()
    #M0 drives the right hand side track i.e. outer side of curve
    #M1 drives the left hand side track i.e. inner side of curve
    #to turn left the right hand side track must turn
    #faster then the left hand side track
    inner_rate=0.5
    outer_rate=0.7
    min_speed = 30
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
  #               to terminate turns after a certain amount of time              #
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
      self.timer = Timer(time,function)
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
    self.evading=True
    action='reverse'
    while self.evading:
      if action=='reverse':
        self.logger.debug('action['+action+']')
        #evasive action starts with reversing
        #until the front sensor no longer sees
        #the obstacle
        self.driveBackwards()
        action='clearObstacle'
      elif action=='clearObstacle':
        self.logger.debug('action['+action+']')
        #we are driving backwards until
        #the sensor no longer detects the
        #obstruction, then we can turn
        if not self.sensorFront.obstructed:
          action='turn'
      elif action=='turn':
        self.logger.debug('action['+action+']')
        #lets make this exciting and decide
        #randomly whether to turn left or right
        direction=['left','right']
        if random.choice(direction)=='left':
          self.turnLeft(3)
        else:
          self.turnRight(3)
        action='turning'
      elif action == 'turning':
        if self.stopped:
          #turn has been executed, evasive
          #action is complete we can go
          #back to driving around at will
          self.evading=False

  #------------------------------------------------------------------------------#
  # driveAvoidCollision: Drive around and avoid collisions                       #
  #                                                                              #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#           
  def driveAvoidCollision(self):
    while True:
      # if we are not stopped, the front sensor is not detecting an
      # obstruction and we are not in the processes of taking evasive
      # action then we can start driving forwards
      if self.stopped and not self.sensorFront.obstructed and not self.evading:
        self.driveForwards()
      # we detected an obstacle, and we are not already taking
      # evasive action than we should go and try to evade the
      # obstacle
      if self.sensorFront.obstructed and not self.evading:
        self.evade() # avoid collision
        
        
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
      self.logger.debug('webServerIp['+str(self.kwargs.get(webServerIp))+'] webServerPort['+ str(self.kwargs.get(webServerPort)) +']')
      httpd.serve_forever()
    finally:
      None
    return 0     
        
#def main():
# ########################
# #GENERAL CONFIGURATION #
# ########################
# #load config
# config=Configuration.general_configuration();
# obstructionSensorFront = Configuration.CONFIG['ObstructionSensors']['FRONT']
#
# ###############
# #SETUP LOGGING#
# ###############
# LOGGER = 'PololuRobot'
# #load logging configuration
# Configuration.logging_configuration();
# #configure logger as per configuration
# Configuration.init_log(LOGGER);
# #create logger
# logger =  logging.getLogger(LOGGER) 
#
# robot = PololuRobot(logger=logger,obstructionSensorFront=int(obstructionSensorFront))
# robot.driveAvoidCollision()
# #robot.driveBackwards()
# #time.sleep(5)
# #robot.turnRight(4)
# #while not robot.stopped:
# #  time.sleep(0.3)
# #time.sleep(3)
# 
# #robot.turnLeft(4)
# #while not robot.stopped:
# #  time.sleep(0.3)
# 
# #robot.driveForwards()
# #time.sleep(5)
# #robot.stop()
# return 0

main=PololuRobot() 
if __name__ == '__main__':
    sys.exit(main())
