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
from state import *
from stored import *
from stage import *
from show import Scene
import xbox
import logging as log

# Operations
OP_PROD = 0x00
OP_TECH = 0x01

# mode masks
#-- normal operation .. no interference
MODE_PASSTHRU    = 0x00
MODE_SCENE_PLAY  = 0x01
MODE_SCENE_EDIT  = 0x02
MODE_STAGE_EDIT  = 0x03

class DmxHandler:
    def __init__(self, config, show, stage_name):
        self.config = config
        self.input = config.input
        self.output = config.output
        self.show = show
        self.stored = Stored()
        self.joy = xbox.Joystick()
        self.stage = self.stored.stage(stage_name)
        self.ctrl_mode = MODE_PASSTHRU

        self.last_mode = 0
        wrapper = ClientWrapper()
        self.tx = wrapper.Client()
    
    def _txDmx(status):
        if status.Succeeded():
            log.debug('Success!')
        else:
            log.error('Error: %s' % status.message)
        
        # TODO -- need this?
        if self.wrapper:
            self.wrapper.Stop()

    def cdata(self,dmx):
        # offset because list indexing starts with 0
        # but dmx id starts with 1
        mode    = dmx[self.input.id-1]
        scene   = dmx[self.input.id]
        fg      = dmx[self.input.id+1]
        return mode, scene, fg


    def handle(self, dmx):
        op, mode, scene = self.cdata(dmx)

        #-- if in tech mode .. controller can init mode change
        #   but the console will be authoritative.
        if op == OP_TECH and mode == MODE_PASSTHRU:
            # allow controller buttons to enter edit modes
            if self.joy.Back():
                if self.ctrl_mode != MODE_SCENE_EDIT:
                    self.ctrl_mode = MODE_SCENE_EDIT
                else: 
                    self.ctrl_mode = MODE_PASSTHRU
            elif self.joy.Home():
                if self.ctrl_mode != MODE_STAGE_EDIT:
                    self.ctrl_mode = MODE_STAGE_EDIT
                else: 
                    self.ctrl_mode = MODE_PASSTHRU
            mode = self.ctrl_mode

        #--- handle logic
        # state change
        if mode != self.last_mode:
            log.debug('mode changed to %d' % mode)
            # load class for working 
            if mode == MODE_STAGE_EDIT: 
                log.debug('mode: stage edit')
                self.working = Stage(self.stage, self.show, self.stored)
            elif mode == MODE_SCENE_EDIT :
                log.debug('mode: scene edit')
                self.working = Scene(self.show, scene)
            elif mode == MODE_SCENE_RUN:
                log.debug('mode: scene run')
                self.working = Scene(self.show, scene)
            else:
                log.debug('mode: passthrough')
#                self.working.close()
                self.working = ''
            self.last_mode = mode

        # handle mode
        if mode & MODE_SCENE_RUN:
            dmx = self.working.run(self.joy, dmx)
        elif ( mode & MODE_STAGE_EDIT or
               mode * MODE_SCENE_EDIT ):
            dmx = self.working.edit(self.joy, dmx)
        
        self.tx.SendDmx(self.output.universe, dmx, self._txDmx)
