# ##############################################################################
# Application         : Pololu Robot 
# Created by          : hta
# Created             : hta
# Changed by          : $Author: b7tarah $
# File changed        : $Date: 2013-08-21 15:19:43 +0200 (Mi, 21 Aug 2013) $
# Environment         : Python 3.3.4
# ##############################################################################
# Description : A simple class representing a sensor used to detected
#               obstructions
#              
################################################################################

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
    self.channel = kwargs.get('obstructionSensorFront',)
    #define obstructed flag    
    self.obstructed = None
    #use Broadcom Pin numbers
    GPIO.setmode(GPIO.BCM)
    #as long as output is high, no obstruction detected
    GPIO.setup(self.channel, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    #initialize state of sensor
    if GPIO.input(self.channel) == GPIO.LOW:
      self.set_obstructed()
    else: # not not obstructed
      self.reset_obstructed()
    #add event to detect falling edge i.e. obstruction detected
    #and to also detect rising edge i.e. no obstruction detected
    GPIO.add_event_detect(self.channel, GPIO.BOTH, callback=self.do_edge)
  def do_edge(self,channel):
    if GPIO.input(self.channel) == GPIO.LOW:
      self.set_obstructed()
    else:
      self.reset_obstructed()
  def set_obstructed(self):
    self.logger.debug('setting obstructed to True')
    self.obstructed=True
  def reset_obstructed(self):
    self.logger.debug('setting obstructed to False')
    self.obstructed=False
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


if __name__ == '__main__':
    sys.exit(main())    
