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
This module implements the ObstructionSensor class. The obstruction sensor is 
attached to the front of the robot and interfaces as an input on channel 4 of 
the GPIO with the raspberry PI, using the RPi.GPIO module.

..http://sourceforge.net/p/raspberry-gpio-python/wiki/Home/
"""

import sys,os,time
import logging
import RPi.GPIO as GPIO
sys.path.append(os.path.join("..","configuration"))
sys.path.append(os.path.join("..","motor control"))
import Configuration

class ObstructionSensor():
  def __init__(self,**kwargs):
    #set our logger
    self.logger = kwargs.get('logger',)
    #which channel is the sensor attached to
    self.channel = int(kwargs.get('obstructionSensorFront'))
    #define obstructed flag    
    self.obstructed = None
    #use Broadcom Pin numbers
    GPIO.setmode(GPIO.BCM)
    #as long as output is high, no obstruction detected
    GPIO.setup(self.channel, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    #initialize state of sensor
    self.do_edge(self.channel)
    #add event to detect falling edge i.e. obstruction detected
    #and to also detect rising edge i.e. no obstruction detected
    GPIO.add_event_detect(self.channel, GPIO.BOTH, callback=self.do_edge)
  #------------------------------------------------------------------------------#
  # do_edge: This function called when either a rising or a falling edge is      #
  #          is detected on our sensor channel                                   #
  #                                                                              #
  # paramteres:  channel: the GPIO channel on wich the edge was detected         #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#     
  def do_edge(self,channel):
    if GPIO.input(self.channel) == GPIO.LOW:
      self.logger.debug('setting obstructed to True')
      self.obstructed=True
    else:
      self.logger.debug('setting obstructed to False')
      self.obstructed=False
      
  #------------------------------------------------------------------------------#
  # cleanUp: Houskeeping, release the resources we used                          #
  #                                                                              #
  #                                                                              #
  # paramteres:                                                                  #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 20.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#        
  def cleanUp(self):  
    GPIO.remove_event_detect(self.channel)
    GPIO.cleanup()
    
def main():
  ########################
  #GENERAL CONFIGURATION #
  ########################
  #load config
  config=Configuration.general_configuration();
  #get sensor parameters
  obstructionSensorFront = Configuration.CONFIG['ObstructionSensors']['FRONT']  

  ###############
  #SETUP LOGGING#
  ###############
  LOGGER = 'ObstructionSensor'
  #load logging configuration
  Configuration.logging_configuration();
  #configure logger as per configuration
  Configuration.init_log(LOGGER);
  #create logger
  logger =  logging.getLogger(LOGGER) 

  #go start application server
  mySensor = ObstructionSensor(logger=logger, obstructionSensorFront=int(obstructionSensorFront))
  
  while True:
    logger.debug('mySensor.obstructed['+str(mySensor.obstructed)+']')
    time.sleep(.5)
  return 0



