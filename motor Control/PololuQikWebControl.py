# ##############################################################################
# Application         : Pololu Robot Webcontrol
# Created by          : hta
# Created             : hta
# Changed by          : $Author: b7tarah $
# File changed        : $Date: 2013-08-21 15:19:43 +0200 (Mi, 21 Aug 2013) $
# Environment         : Python 3.3.4
# ##############################################################################
# Description : A simple application server that presents a website showing
#               a raspicam video stream (assumes mjpg_streamer is setup and
#               running at resultion of 400x300).
#               Furtermore it shows the controls allowing to change direction
#               and speed of the robot
#              
################################################################################

from wsgiref.simple_server import make_server
from  urllib.parse import parse_qs
import logging
import ipaddress
import PololuQikConfig

########################
#GENERAL CONFIGURATION #
########################
#load config
PololuQikConfig.general_configuration();
#set server parameters
webServerIp      = PololuQikConfig.CONFIG['PololuRobotWebControl']['WEB_SERVER_IP']
webServerPort    = PololuQikConfig.CONFIG['PololuRobotWebControl']['WEB_SERVER_PORT']
mjpgStreamServer = PololuQikConfig.CONFIG['PololuRobotWebControl']['MJPG_STREAM_SERVER']

###############
#SETUP LOGGING#
###############
LOGGER = 'pololuQikWebControl'
#load logging configuration
PololuQikConfig.logging_configuration();
#configure logger as per configuration
PololuQikConfig.init_log(LOGGER);
#create logger
logger =  logging.getLogger(LOGGER) 

#Global button colors
backwardButtonColor = None
forwardButtonColor  = None
leftButtonColor     = None
rightButtonColor    = None
stopButtonColor     = None
#init speed
speed = 0

#open and read main page into memory
mainPage    = (open('PololuQikWebControl.html','r').read())
#open and read the control form into memory
controlForm = (open('PololuQikWebControlForm.html','r').read())

#------------------------------------------------------------------------------#
# display_page: load the mainpage. The main page contains an iFrame which      #
#               triggers the consecutive loading of the control form           #
#                                                                              #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 15.05.2014 Initial version                                       #
#------------------------------------------------------------------------------# 
def display_page():
  global mjpgStreamServer
  return mainPage % {'mjpgStreamServer':mjpgStreamServer}

#------------------------------------------------------------------------------#
# display_form: the control form, and set the color of the button text and     #
#               set the message to be shown to the user (if any)               #
# parameters: message: Text message to be shown to user                        #
#             speed  : Speed, value for the slider bar                         #
#             backwardButtonColor, forwardButtonColor, leftButtonColor,        #
#             rightButtonColor, stopButtonColor:                               #
#                      Color for the text on the control buttons. The purpose  #
#                      is to highlight the currently active action suchs as    #
#                      forward, left etc.                                      #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 15.05.2014 Initial version                                       #
#------------------------------------------------------------------------------# 
def display_form(message='',speed='0', backwardButtonColor='black', forwardButtonColor='black', leftButtonColor='black', rightButtonColor='black', stopButtonColor='black'):
  return controlForm % {'message':message, 'speed':speed, 'backwardButtonColor':backwardButtonColor, 'forwardButtonColor':forwardButtonColor, 'leftButtonColor':leftButtonColor, 'rightButtonColor':rightButtonColor, 'stopButtonColor':stopButtonColor}

#------------------------------------------------------------------------------#
# setButtonColors: Set the button colors according to the button pressed by    #
#                  the user, so that the activated action (e.g. forward, left) #
#                  is highlighted                                              #
# parameters: backward: True when backward was chosen, false otherswise        #
#             forward:  True when forward was chosen, false otherswise         #
#             left:     True when left was chosen, false otherswise            #
#             right:    True when right was chosen, false otherswise           #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 15.05.2014 Initial version                                       #
#------------------------------------------------------------------------------# 
def setButtonColors(backward=False, forward=False, left=False, right=False, stop=False):
  activeColor='hotpink'
  normalColor='black'
  if backward:
    return activeColor,normalColor,normalColor,normalColor,normalColor
  elif forward:
    return normalColor,activeColor,normalColor,normalColor,normalColor
  elif left:
    return normalColor,normalColor,activeColor,normalColor,normalColor
  elif right:
    return normalColor,normalColor,normalColor,activeColor,normalColor
  elif stop:
    return normalColor,normalColor,normalColor,normalColor,activeColor
  else:
    return normalColor,normalColor,normalColor,normalColor,normalColor

#------------------------------------------------------------------------------#
# process_form: Processes the user input from the control form, executes the   #
#               desired action (e.g. forward, backward) and give feedback to   #
#               the user indicating what action has been taken                 #
#                  is highlighted                                              #
# parameters: params: dictionary object containing parameters and their values #
#                     from the form.                                           #
#                     action: possbile values: forward, backward, left, right, #
#                                              stop, setSpeed                  #
#                     speed:  possible values: 0-127
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 15.05.2014 Initial version                                       #
#------------------------------------------------------------------------------# 
def process_form(params):
  global logger 
  global backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor
  global speed
  
  action           = params.get('action')[0]
  speedSliderValue = params.get('speed')[0]
  if action == 'forward':
    message='Going '+action
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=False, forward=True, left=False, right=False, stop=False)
    #############################################
    # TODO put code here to drive robot forwards#
    #############################################    
  elif action == 'backward':
    message='Going '+action
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=True, forward=False, left=False, right=False, stop=False)
    ##############################################
    # TODO put code here to drive robot backwards#
    ##############################################    
  elif action == 'left':
    message='Turning '+action    
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=False, forward=False, left=True, right=False, stop=False)
    ########################################
    # TODO put code here to turn robot left#
    ########################################     
  elif action == 'right':
    message='Turning '+action   
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=False, forward=False, left=False, right=True, stop=False)
    #########################################
    # TODO put code here to turn robot right#
    #########################################     
  elif action == 'setSpeed':
    message='Setting speed to '+speedSliderValue
    speed = int(speedSliderValue)
    ######################################
    # TODO put code to set robot velocity#
    ######################################     
  elif action == 'stop':
    message='Stopping'  
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=False, forward=False, left=False, right=False, stop=True)
    ##############################
    # TODO put code to stop robot#
    ##############################     
  
  #return updated control form to web client  
  return display_form (message=message,speed=speedSliderValue,backwardButtonColor=backwardButtonColor,forwardButtonColor=forwardButtonColor,leftButtonColor=leftButtonColor,rightButtonColor=rightButtonColor,stopButtonColor=stopButtonColor)

#------------------------------------------------------------------------------#
# applicationServer: handle requests from web client                           #
# parameters: environ       : environment variables                            #
#             start_response:                                                  #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 15.05.2014 Initial version                                       #
#------------------------------------------------------------------------------# 
def application(environ, start_response):
  global logger
  path_info = environ['PATH_INFO']
  logger.debug('path_info['+path_info+']')
  
  #submit from one of the buttons on the doRobotControl form
  if path_info.endswith('doRobotControl') :
    # for get method, get the parameters from the form
    params = parse_qs(environ['QUERY_STRING'])
    logger.debug(params)
    # process the parameters
    response = process_form(params) 
  #iframe with src=showRobotControlForm must be loaded.
  #Note that this will cause all the buttons to be reset
  #however not the associated actions.So this only works
  #correctly on initial startup. Some work is still 
  #required here
  elif path_info.endswith('showRobotControlForm'):
    response = display_form(backwardButtonColor=backwardButtonColor,forwardButtonColor=forwardButtonColor,leftButtonColor=leftButtonColor,rightButtonColor=rightButtonColor,stopButtonColor=stopButtonColor)
  else:
    #load main paged
    response = display_page()

  start_response('200 OK', [('Content-Type', 'text/html')])

  return [response.encode('utf-8')]

#intialize color of text on buttons to black
backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor=setButtonColors(False,False,False,False,False)
#start application server
server = make_server(str(ipaddress.ip_address(webServerIp)), int(webServerPort), application)
server.serve_forever()
