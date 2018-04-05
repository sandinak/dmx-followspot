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
from show import Fixture

class Stage:
    def __init__(self, stage, show, stored):
        self.stage = stage
        self.show = show
        self.speed = 150
        self.fixtures=dict()
        
        # create objects to work with
        for fname in self.show.fixtures:
            self.fixtures[fname] = Fixture(
                fname, 
                self.show.fixtures[fname], 
                )

        # TODO: create a test for missing values and make that list
        # get a list of fixture_names to order management 
        self.fixture_names = sorted(self.fixtures.iterkeys())
        log.debug(self.fixture_names)

        # set initial fixture pair for editing
        # we set this high cause we access the id using mod(len)
        self.fp_id = (len(self.fixture_names) * 100 ) + 1
        self.set_fp()


    def set_fp(self):
        # -1 because DMX ids are indexed at 1 .. and arrays at 0
        id_a = ((self.fp_id     ) % len(self.fixture_names)) - 1
        id_b = ((self.fp_id + 1 ) % len(self.fixture_names)) - 1
        self.fa = self.fixtures[self.fixture_names[id_a]]
        self.fb = self.fixtures[self.fixture_names[id_b]]

    def edit(self,joy, dmx):
        # rotate thru working pairs
        if joy.leftBumper():
            log.debug(' dec fp: %d' % self.fp_id)
            self.fp_id -= 1
            time.sleep(0.2)
            self.fb.off(dmx)
        elif joy.rightBumper():
            log.debug(' inc fp: %d' % self.fp_id)
            self.fp_id += 1
            time.sleep(0.2)
            self.fa.off(dmx)
        self.set_fp()
        dmx=self.fa.on(dmx)
        dmx=self.fb.on(dmx)
        
        # handle movement
        lx=joy.leftX()
        ly=joy.leftY()
        rx=joy.rightX()
        ry=joy.rightY()
        
        self.fa.x += copysign(lx ** self.speed, lx)
        self.fa.y += copysign(ly ** self.speed, ly) 
        self.fb.x += copysign(rx ** self.speed, rx)
        self.fb.y += copysign(ry ** self.speed, ry)

        for fixture in self.fixtures:
            dmx=self.fixtures[fixture].set_position(dmx)

        return dmx