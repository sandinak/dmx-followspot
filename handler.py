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
import xbox
import logging as log

# binary masks
MODE_PASSTHRU   = 0x00
MODE_RUN        = 0x01
MODE_EDIT_STAGE = 0x02
MODE_EDIT_SCENE = 0x03


class DmxHandler:
    def __init__(self, config, show, stage_name):
        self.config = config
        self.input = config.input
        self.output = config.output
        self.show = show
        self.stored = Stored()
        self.joy = xbox.Joystick()
        self.stage = self.stored.stage(stage_name)
        
        log.debug('stage', self.stage)

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
        mode,scene,fg = self.cdata(dmx)
        #--- handle logic
        # state change
        if mode != self.last_mode:
            log.debug('mode changed to %d' % mode)
            # load class for working 
            if mode & MODE_EDIT_STAGE: 
                self.working = Stage(self.stage, self.show, self.stored)
            elif ( mode & MODE_EDIT_SCENE or
                   mode & MODE_RUN):
                self.working = Scene(stored, scene, dmx)
            else:
                self.working.close()
                self.working = ''
            self.last_mode = mode

        # handle mode
        if mode & MODE_RUN:
            dmx = self.working.run(self.joy, dmx)
        elif ( mode & MODE_EDIT_STAGE or
               mode * MODE_EDIT_SCENE ):
            dmx = self.working.edit(self.joy, dmx)

        self.tx.SendDmx(self.output.universe, dmx, self._txDmx)
