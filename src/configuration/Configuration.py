#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# Application         : Holds, sets and returns globally relevant values
# File                : $HeadURL:  $
# Version             : $Revision: $
# Created by          : hta
# Created             : 01.10.2013
# Changed by          : $Author: b7tarah $
# File changed        : $Date: 2013-08-21 15:19:43 +0200 (Mi, 21 Aug 2013) $
# Environment         : Python 3.2.3 
# ##############################################################################
# Description : holds, sets and returns globally relevant values such as trace
#               level and other command line options that might be required 
#               accross modules. These values should be set only by the
#               init function in the main program, after wich they may only be
#               read.
#
#
################################################################################


import os,sys
import argparse
import collections
import logging, logging.handlers
import configparser

CONFIG = None       #configuration from config.ini
LOGGING= None       #logging configuration from ini file


#------------------------------------------------------------------------------#
# set_CONFIG: set globally available configuration (from config.ini)           #
#                                                                              #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 09.11.2013 Initial version                                       #
#------------------------------------------------------------------------------#
def set_CONFIG(config):
  global CONFIG 
  CONFIG = config
#------------------------------------------------------------------------------#
# get_CONFIG: returns globally available configuration (from config.ini)       #
#                                                                              #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 09.11.2013 Initial version                                       #
#------------------------------------------------------------------------------#
def get_CONFIG():
  global CONFIG
  return CONFIG

#------------------------------------------------------------------------------#
# set_LOGGING: set globally available logging configuration (from logging.ini) #
#                                                                              #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 23.01.2014 Initial version                                       #
#------------------------------------------------------------------------------#
def set_LOGGING(config):
  global LOGGING 
  LOGGING= config
#------------------------------------------------------------------------------#
# get_LOGGING: returns globally available logging configuration                #
#              (from config.ini)                                               # 
#                                                                              #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 09.11.2013 Initial version                                       #
#------------------------------------------------------------------------------#
def get_LOGGING():
  global LOGGING
  return LOGGING
#------------------------------------------------------------------------------#
# init: Read config.ini file                                                   #
#                                                                              #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 17.11.2013 Initial version                                       #
#------------------------------------------------------------------------------#
def general_configuration():
  ###################################
  # get configuration from ini file #
  ###################################
  config = configparser.ConfigParser(allow_no_value=True)
  config.read('../etc/config.ini',encoding='utf-8')
  set_CONFIG(config)
#------------------------------------------------------------------------------#
# init: Read log.ini file. This file whether the various modules should        #
#       write logfiles and if so at what level                                 #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 17.11.2013 Initial version                                       #
#------------------------------------------------------------------------------#
def logging_configuration():
  ##################################
  # Get configuration for loggging #
  ##################################  
  config = configparser.ConfigParser(allow_no_value=True)
  config.read('../etc/log.ini')
  set_LOGGING(config)

#------------------------------------------------------------------------------#
# init: initialize logger                                                      #
#                                                                              #
# Parameters: LOGGER Name of the logger, statically defined in the calling     #
#                    module such as MAIN or WEATHER etc.                       #
#                                                                              #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 17.11.2013 Initial version                                       #
#------------------------------------------------------------------------------#  
def init_log(LOGGER):
  bLogToFile   =False
  bLogToConsole=False
  
  #get logging configuration from log.ini file
  LOGGING=get_LOGGING()
  if LOGGING.getboolean(LOGGER,'log_to_file'): 
    bLogToFile = True
  if LOGGING.getboolean(LOGGER,'log_to_console'): 
    bLogToConsole = True
    
  #################
  # setup logging #
  #################

  # create logger
  logger = logging.getLogger(LOGGER)
  logger.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s')
  
  # create console handler and set level as per configuration
  if bLogToConsole == True:
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, LOGGING[LOGGER]['level'], None)) 
    # add formatter to ch (console handler)
    ch.setFormatter(formatter)
    # add ch and rfh (rotating filehandler to logger
    logger.addHandler(ch)
  
  # create rotating filehandler and set leval as per configuration
  # 10 files, each 10 megabytes.
  if bLogToFile == True:
    rfh = logging.handlers.RotatingFileHandler('../log/'+LOGGER+'.log', 'a', (1024*1024*10), 10)  
    rfh.setLevel(getattr(logging,  LOGGING[LOGGER]['level'], None))
    #add formatter to rotating filehandler
    rfh.setFormatter(formatter)
    #rfh (rotating filehandler to logger
    logger.addHandler(rfh)
  
  # 'application' code
  # logger.debug('debug message')
  # logger.info('info message')
  # logger.warn('warn message')
  # logger.error('error message')
  # logger.critical('critical message')  
  
