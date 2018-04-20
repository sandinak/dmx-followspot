#!/usr/bin/env python
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# dmx_followspot.py
# Copyright (C) 2018 Branson Matheson

import sys
import pprint
from ola.ClientWrapper import ClientWrapper
from show import Scene
import xbox
import logging as log
import time

# Operations
OP_PROD = 0x00
OP_TECH = 0x01

# mode masks
#-- normal operation .. no interference
MODE_PASSTHRU = 0x00
MODE_SCENE_RUN = 0x01
MODE_SCENE_EDIT = 0x02
MODE_STAGE_EDIT = 0x03


class DmxHandler:
    def __init__(self, config, show, stage, joy):
        self.config = config
        self.input = config.input
        self.output = config.output
        self.show = show
        self.stage = stage
        self.joy = joy

        # define base setup
        self.mode = OP_PROD
        self.joy_mode = OP_PROD
        self.op = MODE_PASSTHRU

        # define tracking
        self.last_mode = 0
        self.last_op = 0
        self.last_scene = 0

        log.info('starting DMX handler op: %d, mode: %d' % (
            self.op, self.mode))
        wrapper = ClientWrapper()
        self.tx = wrapper.Client()

    def _txDmx(status):
        ''' handle DMX send issues '''
        if status.Succeeded():
            log.debug('Success!')
        else:
            log.error('Error: %s' % status.message)

        # TODO -- need this?
        if self.wrapper:
            self.wrapper.Stop()

    def read_dmx(self):
        ''' 
        read controller data from DMX data
            - offset because list indexing starts with 0
              but dmx id starts with 1
        '''
        dmx_i = self.input.id - 1
        self.op =       self.dmx[dmx_i]
        self.mode =     self.dmx[dmx_i + 1]
        self.scene =    self.dmx[dmx_i + 2]

    def read_joy_mode_changes(self):
        # log.debug('joystick input %s' % self.joy.reading)
        # allow controller buttons to enter edit modes
        if self.op == OP_PROD:
            # do nothing if in production mode
            return

        if self.joy.Start() and self.joy_mode == MODE_PASSTHRU:
            self.joy_mode = MODE_SCENE_EDIT

        elif self.joy.Guide() and self.joy_mode == MODE_PASSTHRU:
            self.joy_mode = MODE_STAGE_EDIT
            
        elif self.joy.Back():
            self.joy_mode = MODE_PASSTHRU
            

    def op_change(self):
        ''' 
        handle operation change. 
        '''
        if self.mode & OP_PROD:
            log.info('operation changed to Production.')
        elif self.mode & OP_TECH:
            log.info('operation changed to Technical Editing.')

    def mode_change(self):
        ''' 
        handle mode changes, we do this by loading a class
        on self.working that will have methods for operation
        '''
        log.debug('mode changed to %d' % self.mode)
        if self.mode == MODE_STAGE_EDIT:
            log.debug('mode: stage edit %s ' % self.stage.name )
            self.working = Stage(self.stage, self.show, self.stored)
            self.joy.led(10)

        elif (self.mode == MODE_SCENE_EDIT or
              (self.mode == MODE_SCENE_EDIT and
                self.scene != self.last_scene)):
            log.debug('mode: scene edit %s' % self.scene)
            self.working = Scene(self.show, self.scene)
            self.joy.led(13)

        elif (self.mode == MODE_SCENE_RUN or
              (self.mode == MODE_SCENE_RUN and
                self.scene != self.last_scene)):
            log.debug('mode: scene run %s ' % self.scene)
            self.working = Scene(self.show, self.scene)
            self.joy.led(1) 

        else:
            log.debug('mode: passthrough')
            self.joy.led(self.config.joystick['id'] + 1)
            del self.working

    def handle(self, dmx):
        ''' 
        handler callback for DMX input
        '''
        self.dmx = dmx

        # read DMX mode changes
        self.read_dmx()

        # read joystick mode changes
        if self.joy.refresh():
            log.debug('joystick change %s' % self.joy.reading )
            self.read_joy_mode_changes()

        # joystick overrides console in Tech mode
        if (self.op == OP_TECH and
            self.joy != MODE_PASSTHRU ):
            self.mode = self.joy_mode

        # handle logic changes,
        # the sleep is to prevent button bounce.
        if self.op != self.last_op:
            self.op_change()
            time.sleep(.2)
            self.last_op = self.op
        if self.mode != self.last_mode:
            self.mode_change()
            time.sleep(.2)
            self.last_mode = self.mode
            self.last_scene = self.scene

        # handle operation based on mode.
        if self.mode & MODE_SCENE_RUN:
            self.dmx = self.working.run(self.joy, self.dmx)
        elif (self.mode & MODE_STAGE_EDIT or
              self.mode * MODE_SCENE_EDIT):
            self.dmx = self.working.edit(self.joy, self.dmx)

        self.tx.SendDmx(self.output.universe, self.dmx, self._txDmx)
