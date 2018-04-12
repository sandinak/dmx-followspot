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

import copy
import logging as log
import time
import math
import numpy
from show import Fixture
from show import FixtureGroup
from show import Target

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class Stage:
    def __init__(self, stage, show, stored):
        self.stage = stage
        self.show = show
        self.speed = 100
        self.fixtures=dict()
        self.all_lights = False
        
        # create objects to work with
        # TODO: add stored info here.
        for fname in self.show.fixtures:
            self.fixtures[fname] = Fixture( self.show, fname)
        self.fp = FixturePair(self.fixtures)
        
    def handle_fp_cmds(self, joy):
        # rotate thru working pairs
        if joy.leftBumper():
            log.debug('dec fp')
            self.fp.b.off()
            self.fp.prev()
            time.sleep(0.2)

        elif joy.rightBumper():
            log.debug('inc fp')
            self.fp.a.off()
            self.fp.next()
            self.fp.set_pair()
            time.sleep(0.2)

        if joy.dpadRight():
            self.fp.a.update_focus(+8)
        elif joy.dpadLeft():
            self.fp.a.update_focus(-8)

    def handle_movement(self, joy):
        # change speed
        if joy.dpadUp():
            self.speed = clamp(self.speed+50, 25, 500)
            log.debug(' inc speed: %d' % self.speed)

        elif joy.dpadDown():
            self.speed = clamp(self.speed-50, 25, 500)
            log.debug(' dec speed: %d' % self.speed)
         # handle movement
        lx = joy.leftX()
        ly = joy.leftY()
        rx = joy.rightX()
        ry = joy.rightY()
        if lx or ly:
            self.fp.a.update_coordinates(
                (self.speed * lx), 
                (self.speed * ly))
        if rx or ry: 
            self.fp.b.update_coordinates(
                (self.speed * rx), 
                (self.speed * ry))

    def handle_lights(self,joy):
        # handle light 
        if self.all_lights ==  False and joy.rightTrigger():
            self.all_lights = True
            self.fixtures[fixture].on()
            log.debug('all_on')
            time.sleep(0.2)

        elif self.all_lights == True and joy.rightTrigger():
            self.all_lights = False
            self.fixtures[fixture].off()
            log.debug('all_off')
            time.sleep(0.2)


    def edit(self, joy, dmx):
        self.handle_fp_cmds(joy)
        self.handle_movement(joy)
        self.handle_lights(joy)

        # walk the fixtures and handle any all config
        for fixture in self.fixtures:
            dmx = self.fixtures[fixture].update_dmx(dmx)
        return dmx

    
class FixturePair(Stage):
    def __init__(self, fixtures):
        self.fixtures = fixtures
        self.fixture_names = sorted(self.fixtures.iterkeys())

        #  TODO: set flags on fixtures that need edits
        self.id = (len(self.fixture_names) * 100 ) + 1
        self.set_pair()
        
    def prev(self):
        self.id = (self.id-1) % len(self.fixture_names)
        self.set_pair()
    
    def next(self):
        self.id = (self.id+1) % len(self.fixture_names)
        self.set_pair()
    
    def set_pair(self):
        # -1 because DMX ids are indexed at 1 .. and arrays at 0
        id_a = ((self.id     ) % len(self.fixture_names)) - 1
        id_b = ((self.id + 1 ) % len(self.fixture_names)) - 1
        log.debug('fp: %d %d' % ( id_a, id_b))
        self.a = self.fixtures[self.fixture_names[id_a]]
        self.b = self.fixtures[self.fixture_names[id_b]]
        if self.a.located() and self.b.located():
        
            self.a.point_to(self.b)
            self.b.point_to(self.a)
        self.on()

    def on(self):
        self.a.on()
        self.b.on()
        
    def locate(self):
        if self.a.located and self.b.located:
            self.a.point_to(self.b.location)
            self.b.point_to(self.a.location)
