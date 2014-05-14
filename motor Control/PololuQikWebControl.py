from wsgiref.simple_server import make_server
from  urllib.parse import parse_qs
import logging
import PololuQikConfig


LOGGER = 'application'

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

#read
html_page = (open('PololuQikWebControl.html','r').read())


def display_form(message='',speed='0', backwardButtonColor='black', forwardButtonColor='black', leftButtonColor='black', rightButtonColor='black', stopButtonColor='black'):
  return html_page % {'message':message, 'speed':speed, 'backwardButtonColor':backwardButtonColor, 'forwardButtonColor':forwardButtonColor, 'leftButtonColor':leftButtonColor, 'rightButtonColor':rightButtonColor, 'stopButtonColor':stopButtonColor}

# the logic
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
    
def process_form(params):
  global logger 
  global backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor
  speed=0

  direction        = params.get('direction')[0]
  speedSliderValue = params.get('speed')[0]
  if direction == 'forward':
    message='Going '+direction
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=False, forward=True, left=False, right=False, stop=False)
    
  elif direction == 'backward':
    message='Going '+direction
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=True, forward=False, left=False, right=False, stop=False)
  elif direction == 'left':
    message='Turning '+direction    
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=False, forward=False, left=True, right=False, stop=False)
  elif direction == 'right':
    message='Turning '+direction   
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=False, forward=False, left=False, right=True, stop=False)
  elif direction == 'setSpeed':
    message='Setting speed to '+speedSliderValue
    speed = int(speedSliderValue)
  elif direction == 'stop':
    speed = 0
    message='Stopping'  
    backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor = setButtonColors(backward=False, forward=False, left=False, right=False, stop=True)
    
  return display_form (message=message,speed=speedSliderValue,backwardButtonColor=backwardButtonColor,forwardButtonColor=forwardButtonColor,leftButtonColor=leftButtonColor,rightButtonColor=rightButtonColor,stopButtonColor=stopButtonColor)
  
def application(environ, start_response):
  global logger
  path_info = environ['PATH_INFO']
  logger.debug('path_inof['+path_info+']')
  #req_size = int(environ['CONTENT_LENGTH'])  
  if path_info.endswith('control') :
    # for post method, params in an input stream of bytes 
    # using decode() to convert to string
    #params = parse_qs(environ['wsgi.input'].read(req_size).decode())
    # for get method
    params = parse_qs(environ['QUERY_STRING'])
    logger.debug(params)
    response = process_form(params)    
  else:
    response = display_form()

  response_headers = [('Content-Type', 'text/html')]
  start_response('200 OK', [('Content-Type', 'text/html')])

  return [response.encode('utf-8')]
  
backwardButtonColor,forwardButtonColor,leftButtonColor,rightButtonColor,stopButtonColor=setButtonColors(False,False,False,False,False)    
server = make_server('10.0.0.100', 8051, application)
server.serve_forever()
