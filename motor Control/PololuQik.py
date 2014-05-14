# ##############################################################################
# Application         : Pololu QIK 2S9V1 Dual serial motor controller
# Created by          : hta
# Created             : hta
# Changed by          : $Author: b7tarah $
# File changed        : $Date: 2013-08-21 15:19:43 +0200 (Mi, 21 Aug 2013) $
# Environment         : Python 3.3.4
# ##############################################################################
# Description : A simple class which lets you configure and control the  
#               pololu QIK 2S9V1 Dual serial motor controller.
#               This class is based on Pololu's Arduino library for the Pololu 
#               qik dual serial motor controllers see alsoe 
#               https://github.com/pololu/qik-arduino/tree/master/PololuQik
#              
#              
#
#
################################################################################

import logging,traceback
import serial
import time
import PololuQikConfig

# Commands
QIK_AUTODETECT_BAUD_RATE         = 0xAA

QIK_GET_FIRMWARE_VERSION         = 0x81
QIK_GET_ERROR_BYTE               = 0x82
QIK_GET_CONFIGURATION_PARAMETER  = 0x83
QIK_SET_CONFIGURATION_PARAMETER  = 0x84
                                 
QIK_MOTOR_M0_FORWARD             = 0x88
QIK_MOTOR_M0_FORWARD_8_BIT       = 0x89
QIK_MOTOR_M0_REVERSE             = 0x8A
QIK_MOTOR_M0_REVERSE_8_BIT       = 0x8B
QIK_MOTOR_M1_FORWARD             = 0x8C
QIK_MOTOR_M1_FORWARD_8_BIT       = 0x8D
QIK_MOTOR_M1_REVERSE             = 0x8E
QIK_MOTOR_M1_REVERSE_8_BIT       = 0x8F


QIK_2S9V1_MOTOR_M0_COAST         = 0x86
QIK_2S9V1_MOTOR_M1_COAST         = 0x87

# Configuration parameters
QIK_CONFIG_DEVICE_ID                       =  0
QIK_CONFIG_PWM_PARAMETER                   =  1
QIK_CONFIG_SHUT_DOWN_MOTORS_ON_ERROR       =  2
QIK_CONFIG_SERIAL_TIMEOUT                  =  3

# name of logger
LOGGER = 'PololuQik'

class PololuQik():
 
      
  def __init__(self):
    #load general configuration
    PololuQikConfig.general_configuration();
    #load logging configuration
    PololuQikConfig.logging_configuration();
    #configure logger as per configuration
    PololuQikConfig.init_log(LOGGER);
    #create logger
    self.logger =  logging.getLogger(LOGGER)
    #create serial  connection  
    serialPort=PololuQikConfig.CONFIG['PololuQik']['SERIAL_PORT']
    self.logger.debug('using serial port['+serialPort+']')    
    self.ser = serial.Serial(serialPort, 38400)
    # wait for connection to intialize
    time.sleep(1)
    # not interested in whatever is in the input buffer
    self.ser.flushInput()    
    # create empty byte array for qik commands
    self.write_bytes = bytearray()
    # let device detect baud rate and start normal oparation
    self.autoDetectBaudRate()
  
  #------------------------------------------------------------------------------#
  # autoDetectBaudRate: triggers the qik controller to detect baud rate and enter#
  #                     normal operating mode.                                   #
  #                     I.e. the green LED should change from continuous blinking#
  #                     to a short flash aprox. every two seconds.               #
  #                                                                              #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#  
  def autoDetectBaudRate(self):
    #clear byte array
    self.write_bytes.clear()
    #set command byte
    self.write_bytes.append(QIK_AUTODETECT_BAUD_RATE)
    # Write the byte to the serial port
    self.ser.write(self.write_bytes)
    
  #------------------------------------------------------------------------------#
  # getFirmwareVersion: retrieve firmware version from qik controller            #
  #                                                                              #
  # Parameters: none                                                             #
  #                                                                              #
  # returnvalues: returnInt  Interger value of firmware version                  #
  #               returnChar String represnting value of firmware version        #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#      
  def getFirmwareVersion(self):
    #clear byte array
    self.write_bytes.clear()
    #set command byte
    self.write_bytes.append(QIK_GET_FIRMWARE_VERSION)
    # Write the byte to the serial port
    self.ser.write(self.write_bytes)
    # Wait for response
    response = self.ser.read()
    try:
      returnInt  = ord(response)
      returnChar = response.decode('ascii').strip()
      self.logger.debug('response value[' + str(returnInt) + '], ascii character[' + returnChar + ']')
      return returnInt,returnChar
    except Exception:
      self.logger.error('unexpected error ['+  str(traceback.format_exc()) +']')
      
  #------------------------------------------------------------------------------#
  # getErrorByte: get error byte from qik controller                             #
  #                                                                              #
  # Parameters: none                                                             #
  #                                                                              #
  # returnvalues: returnInt:  Integer value representing the error byte          #
  #                 bit 0 (lsb): unused                                          #
  #                 bit 1:       unused                                          #
  #                 bit 2:       unused                                          #
  #                 bit 3:       Data Overrun Error                              #
  #                 bit 4:       Frame Error                                     #
  #                 bit 5:       CRC Error                                       #
  #                 bit 6:       Format Error                                    #
  #                 bit 7:       Timeout                                         #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#        
  def getErrorByte(self):
    #clear byte array
    self.write_bytes.clear()
    #set command byte
    self.write_bytes.append(QIK_GET_ERROR_BYTE)
    # Write the byte to the serial port
    self.ser.write(self.write_bytes)
    # Wait for response
    response = self.ser.read(1)
    try:
      returnInt  = ord(response)
      self.logger.debug('error byte[' +'{:08b}'.format(returnInt) + ']')
      return returnInt
    except Exception:
      self.logger.error('unexpected error ['+  str(traceback.format_exc()) +']')

  #------------------------------------------------------------------------------#
  # getConfigurationParameter: get the value of a configuration parameter        #
  #                                                                              #
  # Parameters: param: 0 Device ID (default 9)                                   #
  #                    1 PWM Parameter (default 0)                               #
  #                    2 Shutdown motors on error (default 1)                    #
  #                    3 Serial Timeout (default 0)                              #
  #                                                                              #
  # returnvalues: returnInt:  Integer value representing parameter value         #
  #               returnChar: ASCII character representing parameter value       #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#  
  def getConfigurationParameter(self, param):
    #clear byte array
    self.write_bytes.clear()
    #set command byte
    self.write_bytes.append(QIK_GET_CONFIGURATION_PARAMETER)
    #select parameter value to retrieve
    self.write_bytes.append(param)
    
    # Write the bytes to the serial port
    self.ser.write(self.write_bytes)
    # Wait for response
    response = self.ser.read(1)
    try:
      returnInt  = ord(response)
      returnChar = response.decode('ascii').strip()
      self.logger.debug('requested parameter[' + str(param) + '] response value[' + str(returnInt) + '], ascii character[' + returnChar + ']')
      return returnInt,returnChar
    except Exception:
      self.logger.error('unexpected error ['+  str(traceback.format_exc()) +']')
      
  #------------------------------------------------------------------------------#
  # setConfigurationParameter: set the value of a configuration parameter        #
  #                                                                              #
  # Parameters: param: 0 Device ID (default 9)                                   #
  #                    1 PWM Parameter (default 0)                               #
  #                    2 Shutdown motors on error (default 1)                    #
  #                    3 Serial Timeout (default 0)                              #
  #             value: Desired value for the chosen parameter                    #
  #                                                                              #
  # returnvalues: returnInt:  0: Command OK (success)                            #
  #                           1: Bad Parameter (invalid parameter number)        #
  #                           2: Bad Value (invalid value for parameter)         #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#      
  def setConfigurationParameter(self, param, value):
    #clear byte array
    self.write_bytes.clear()
    #set command byte
    self.write_bytes.append(QIK_SET_CONFIGURATION_PARAMETER)
    #select parameter to set
    self.write_bytes.append(param)
    #the desired parameter value
    self.write_bytes.append(value)
    #terminate set configuration sequence
    self.write_bytes.append(0x55)    
    self.write_bytes.append(0x2A)    
    # Write the bytes to the serial port
    self.ser.write(self.write_bytes)
    # Wait for response
    response = self.ser.read(1)
    try:
      returnInt  = ord(response)
      returnChar = response.decode('ascii').strip()
      self.logger.debug('requested parameter[' + str(param) + '] / value[' + str(value) + '], response[' + str(returnInt) + ']')
      return returnInt,returnChar
    except Exception:
      self.logger.error('unexpected error ['+  str(traceback.format_exc()) +']')      

  #------------------------------------------------------------------------------#
  # setM0Coast: set Motor 0 to coast                                             #
  #                                                                              #
  # Parameters: None                                                             #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#
  def setM0Coast(self):
    #clear byte array
    self.write_bytes.clear()
    #set command byte
    self.write_bytes.append(QIK_2S9V1_MOTOR_M0_COAST)
    # Write the byte to the serial port
    self.ser.write(self.write_bytes)

  #------------------------------------------------------------------------------#
  # setM1Coast: set Motor 1 to coast                                             #
  #                                                                              #
  # Parameters: None                                                             #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#
  def setM1Coast(self):
    #clear byte array
    self.write_bytes.clear()
    #set command byte
    self.write_bytes.append(QIK_2S9V1_MOTOR_M1_COAST)
    # Write the byte to the serial port
    self.ser.write(self.write_bytes)

  #------------------------------------------------------------------------------#
  # setCoast: set both motors to coast                                           #
  #                                                                              #
  # Parameters: None                                                             #
  #                                                                              #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#
  def setCoast(self):
    #clear byte array
    self.setM0Coast()
    self.setM1Coast()

  #------------------------------------------------------------------------------#
  # setM0Speed: set speed for motor 0. Use positive speeds for forward motion,   #
  #             use negative speeds for reverse                                  #
  # Parameters: speed: -255..255 (when 8 bit mode configured)                    #
  #                    -127..127 (when 7 bit mode configured)                    #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#
  def setM0Speed(self, speed):
    #clear byte array
    self.write_bytes.clear()
    #initialize reverse 
    reverse = False
    if speed < 0 :
      speed = -1 * speed # make speed a positive number
      reverse = True # preserve direction
    
    if speed > 255 :
      speed = 255
    
    if speed > 127 : 
      # 8-bit mode: actual speed is (speed + 128) 
      if reverse :
        self.write_bytes.append(QIK_MOTOR_M0_FORWARD_8_BIT)
      else:
        self.write_bytes.append(QIK_MOTOR_M0_REVERSE_8_BIT)
      self.write_bytes.append(speed - 128)
    else:
      if reverse :
        self.write_bytes.append(QIK_MOTOR_M0_FORWARD)
      else:
        self.write_bytes.append(QIK_MOTOR_M0_REVERSE)
      self.write_bytes.append(speed)
      
    # Write the bytes to the serial port
    self.ser.write(self.write_bytes)

  #------------------------------------------------------------------------------#
  # setM1Speed: set speed for motor 1. Use positive speeds for forward motion,   #
  #             use negative speeds for reverse                                  #
  # Parameters: speed: -255..255 (when 8 bit mode configured)                    #
  #                    -127..127 (when 7 bit mode configured)                    #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#
  def setM1Speed(self, speed):
    #clear byte array
    self.write_bytes.clear()
    #initialize reverse 
    reverse = False
    if speed < 0 :
      speed = -1 * speed # make speed a positive number
      reverse = True # preserve direction
    
    if speed > 255 :
      speed = 255
    
    if speed > 127 : 
      # 8-bit mode: actual speed is (speed + 128) 
      if reverse :
        self.write_bytes.append(QIK_MOTOR_M1_REVERSE_8_BIT)
      else:
        self.write_bytes.append(QIK_MOTOR_M1_FORWARD_8_BIT)
      self.write_bytes.append(speed - 128)
    else:
      if reverse :
        self.write_bytes.append(QIK_MOTOR_M1_REVERSE)
      else:
        self.write_bytes.append(QIK_MOTOR_M1_FORWARD)
      self.write_bytes.append(speed)
      
    # Write the bytes to the serial port
    self.ser.write(self.write_bytes)  

  #------------------------------------------------------------------------------#
  # setSpeed: set speed for both motors. Use positive speeds for forward motion, #
  #             use negative speeds for reverse                                  #
  # Parameters: speed: -255..255 (when 8 bit mode configured)                    #
  #                    -127..127 (when 7 bit mode configured)                    #
  # returnvalues: None                                                           #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 12.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------#
  def setSpeed(self, speed) :
    self.setM0Speed(speed)
    self.setM1Speed(speed)
      
def main():
  qik=PololuQik()
  version=qik.getFirmwareVersion()
  errorByte=qik.getErrorByte()
  parameterValue=qik.getConfigurationParameter(0x03)
  #returnValue=qik.setConfigurationParameter(0x03,0x00)
  qik.setSpeed(-127)
  time.sleep(3)
  qik.setCoast()
if __name__ == '__main__':
  main()      
  
