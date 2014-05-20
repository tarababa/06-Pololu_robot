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
from threading import Timer
sys.path.append(os.path.join('..','motor control'))
sys.path.append(os.path.join('..','configuration'))
import PololuQik, Configuration, ObstructionSensor    
    
class PololuRobot():
  def __init__(self,**kwargs):
    self.timer=None
    #get logger object which is passed
    #as a parameter
    self.logger=kwargs.get('logger',)
    #there is one obstruction sensor a
    #at the front of the robot
    #self.sensorFront=ObstructionSensor(**kwargs)
    #we have one motor controller for
    #both motors
    self.motorControl=PololuQik.PololuQik()
    self.setDriveSpeed=30
    #initially the robot is stopped
    self.stopped=True
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
    self.stoppped=False
    
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
    self.stoppped=False
    
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
    self.stoppped=True
    
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
    self.stoppped=False
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
    self.stoppped=False
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
  #                 cancelled
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


def main():
  ########################
  #GENERAL CONFIGURATION #
  ########################
  #load config
  config=Configuration.general_configuration();

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

  robot = PololuRobot(logger=logger)
  
  #robot.driveBackwards()
  #time.sleep(5)
  robot.turnRight(4)
  while not robot.stopped:
    time.sleep(0.3)
  time.sleep(3)
  
  robot.turnLeft(4)
  while not robot.stopped:
    time.sleep(0.3)
  
  #robot.driveForwards()
  #time.sleep(5)
  #robot.stop()
  return 0


if __name__ == '__main__':
    sys.exit(main())