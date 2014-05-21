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
This module implements the PololuRobotWebControlApp class. This module serves up
the web page which can be used to control the PololuRobot and shows video stream
from the camera attached to the raspberry pi.

The web application is assumed to be single user and uses 'wheezy.routing' to 
handle URL processing, and 'WebOb''s Request and Response classes
to ease construction of the responses. The pages themselves are stored as HTML
with placeholders which are replaced as required

.. wheezy.routing: http://pythonhosted.org/wheezy.routing/
.. WebOb: http://webob.org/
"""

import sys,os
from wsgiref.simple_server import make_server
import logging
from wheezy.routing import PathRouter, url
from webob import Request, Response, exc

sys.path.append(os.path.join("..","configuration"))
import Configuration

#determine location of this file
HERE = os.path.abspath(os.path.dirname(__file__))
#text labels for roving on/off toggle button
ROVING_ON = 'Roving ON'
ROVING_OFF= 'Roving OFF'
#------------------------------------------------------------------------------#
# WebControlFormHelper: helper class, holds pages and dynamic items on pages   #
#                                                                              #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 15.05.2014 Initial version                                       #
#------------------------------------------------------------------------------# 
class WebControlFormHelper():
  def __init__(self,**kwargs):
    #set HTML dir 
    html_dir = os.path.abspath( os.path.join(HERE, 'html'))    
    #open and read main page into memory (TODO make this more generic)
    self.mainPage    = (open(html_dir+'/PololuQikWebControl.html','r').read())
    #open and read the control form into memory
    self.controlForm = (open(html_dir+'/PololuQikWebControlForm.html','r').read())
    self.backwardButtonColor     = None
    self.forwardButtonColor      = None
    self.leftButtonColor         = None
    self.rightButtonColor        = None
    self.stopButtonColor         = None
    self.toggleRovingButtonColor = None
    self.toggleRovingButtonText  = None
    self.message                 = None
    self.speed                   = 0
    self.mjpgStreamServer = kwargs.get('mjpgStreamServer','http://10.0.0.101:8080/?action=stream')
    self.setButtonColors()
  #------------------------------------------------------------------------------#
  # setButtonColors: Set the button colors according to the button pressed by    #
  #                  the user, so that the activated action (e.g. forward, left) #
  #                  is highlighted                                              #
  # parameters: backward: True when backward was chosen, false otherswise        #
  #             forward:  True when forward was chosen, false otherswise         #
  #             left:     True when left was chosen, false otherswise            #
  #             right:    True when right was chosen, false otherswise           #
  #             stop:     True when stop was chosen, false otherswise            #
  #             roving:   True when roving was chosen, false otherswise          #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 15.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------# 
  def setButtonColors(self,backward=False, forward=False, left=False, right=False, stop=False, roving=False):
    activeColor='hotpink'
    normalColor='black'
    self.backwardButtonColor     = normalColor
    self.forwardButtonColor      = normalColor
    self.leftButtonColor         = normalColor
    self.rightButtonColor        = normalColor
    self.stopButtonColor         = normalColor
    self.toggleRovingButtonColor = normalColor
    self.toggleRovingButtonText  = ROVING_OFF
    if backward:
      self.backwardButtonColor     = activeColor
    elif forward:                 
      self.forwardButtonColor      = activeColor
    elif left:                    
      self.leftButtonColor         = activeColor
    elif right:                   
      self.rightButtonColor        = activeColor
    elif stop:                    
      self.stopButtonColor         = activeColor
    elif roving:
      self.toggleRovingButtonColor = activeColor
      self.toggleRovingButtonText  = ROVING_ON

#------------------------------------------------------------------------------#
# PololuRobotWebControlApp: handle requests from web client                    #
#                                                                              #
#------------------------------------------------------------------------------#
# version who when       description                                           #
# 1.00    hta 15.05.2014 Initial version                                       #
#------------------------------------------------------------------------------# 
class PololuRobotWebControlApp(object):
  def __init__(self, **kwargs):
    self.form = WebControlFormHelper(**kwargs)
    self.logger = kwargs.get('logger',)
    self.robot = kwargs.get('robot')
    #initialize speed in form with robot speed
    self.form.speed = self.robot.setDriveSpeed
    #create routes to web pages
    self.router = PathRouter()
    self.router.add_routes([
      url('/', self.do_main_page, name='home'),
      url('/doRobotControl', self.do_process_form, name='execute'),
      url('/showRobotControlForm', self.do_display_form, name='view')
      ])

  def __call__(self, environ, start_response):
    req = Request(environ)
    try:
      handler, kwargs = self.router.match(req.path_info)
      if handler:
        # XXX Why does route_name only appear in kwargs sometimes?!
        if 'route_name' in kwargs:
            del kwargs['route_name']
        resp = handler(req, **kwargs)
      else:
        self.not_found(req)
    except exc.HTTPException as e:
      # The exception itself is a WSGI response
      resp = e
    return resp(environ, start_response)

  def not_found(self, req):
    """Handler for unknown locations (404)"""
    raise exc.HTTPNotFound('The resource at %s could not be found' % req.path_info)


  #------------------------------------------------------------------------------#
  # do_main_page: load the mainpage. The main page contains an iFrame which      #
  #               triggers the consecutive loading of the control form           #
  #               The main page contains a link to mjpgStreamServer, which shows #
  #               a video stream from the attached raspicam. The url for this    #
  #               server is configured in etc/config.ini                         #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 15.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------# 
  def do_main_page(self, req):
    res = Response()
    res.content_type = 'text/html'
    res.text         = self.form.mainPage % {'mjpgStreamServer':self.form.mjpgStreamServer}
    return res

  #------------------------------------------------------------------------------#
  # do_display_form: the control form, and set the color of the button text and  #
  #                  set the message to be shown to the user (if any)            #
  # parameters: message: Text message to be shown to user                        #
  #             speed  : Speed, value for the slider bar                         #
  #             toggleRovingButtonText: Roving OFF, Roving ON                   #
  #             backwardButtonColor, forwardButtonColor, leftButtonColor,        #
  #             rightButtonColor, stopButtonColor, toggleRovingButtonColor:     #
  #                      Color for the text on the control buttons. The purpose  #
  #                      is to highlight the currently active action suchs as    #
  #                      forward, left etc.                                      #
  #------------------------------------------------------------------------------#
  # version who when       description                                           #
  # 1.00    hta 15.05.2014 Initial version                                       #
  #------------------------------------------------------------------------------# 
  def do_display_form(self, req):
    res = Response()
    res.content_type = 'text/html'
    res.text         = self.form.controlForm % {'message':self.form.message, 
                                    'speed':  self.form.speed, 
                                    'backwardButtonColor':     self.form.backwardButtonColor, 
                                    'forwardButtonColor':      self.form.forwardButtonColor, 
                                    'leftButtonColor':         self.form.leftButtonColor, 
                                    'rightButtonColor':        self.form.rightButtonColor, 
                                    'stopButtonColor':         self.form.stopButtonColor,
                                    'toggleRovingButtonColor': self.form.toggleRovingButtonColor,
                                    'toggleRovingButtonText':  self.form.toggleRovingButtonText}   
    return res
    
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
  def do_process_form(self, req):
    
    action           = req.params['action'] 
    speedSliderValue = req.params['speed']
    self.logger.debug('action['+action+'] speedSliderValue['+speedSliderValue+']')
    if action == 'forward':
      self.form.message='Going '+action
      self.form.setButtonColors(backward=False, forward=True, left=False, right=False, stop=False, roving=False)
      self.robot.stopRoving()
      self.robot.driveForwards()
    elif action == 'backward':
      self.form.message='Going '+action
      self.form.setButtonColors(backward=True, forward=False, left=False, right=False, stop=False, roving=False)
      self.robot.stopRoving()
      self.robot.driveBackwards()
    elif action == 'left':
      self.form.message='Turning '+action    
      self.form.setButtonColors(backward=False, forward=False, left=True, right=False, stop=False, roving=False)
      self.robot.stopRoving()
      self.robot.turnLeft()
    elif action == 'right':
      self.form.message='Turning '+action   
      self.form.setButtonColors(backward=False, forward=False, left=False, right=True, stop=False, roving=False)
      self.robot.stopRoving()
      self.robot.turnRight()
    elif action == 'setSpeed':
      self.form.message='Setting speed to '+speedSliderValue
      self.form.speed = int(speedSliderValue)
      self.robot.setSpeed(self.form.speed)
    elif action == 'stop':
      self.form.message='Stopping'  
      self.form.setButtonColors(backward=False, forward=False, left=False, right=False, stop=True, roving=False)
      self.robot.stop()
      if self.robot.isRoving:
        self.robot.stopRoving()
    elif action == 'roving':
      #Toggle roving, of roving on then turn it of and vice versa
      if self.robot.isRoving:
        self.form.message='End roving'  
        self.form.setButtonColors(backward=False, forward=False, left=False, right=False, stop=False, roving=False)
        self.robot.stopRoving()
      else:
        self.form.message='Start roving'  
        self.form.setButtonColors(backward=False, forward=False, left=False, right=False, stop=False, roving=True)      
        self.robot.runRoving()
    #return updated control form to web client  
    return self.do_display_form (req)




