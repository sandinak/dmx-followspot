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

import logging as log

class Fixture:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.type = self.data['type']
        self.id = self.data['id']
        self.profile = self.data['profile']
        self.x_range = self.profile['x-range']
        self.y_range = self.profile['y-range']
        self.channels = self.profile['channels']
        self.managed_attributes = self.profile['managed_attributes']
        self.x = (255*255)/2
        self.y = (255*255)/2
        self.dmx = dict()

        if 'color_values' in self.profile:
            self.color_values = self.profile['color_values']

        # init map values
        for c in self.channels:
            self.dmx[c] = 0
        
    def update(self, dmx):
        for c in self.channels:
            dmx_i = self.id + self.channels.index(c) - 1
            dmx[dmx_i] = self.dmx[c]
        return dmx
        
    def get_position(self, dmx):
        if 'x-coarse' in self.dmx:
            x = ((self.dmx['x-coarse'] * 255) + self.dmx['x-fine'])
            y = ((self.dmx['y-coarse'] * 255) + self.dmx['y-fine'])
        else: 
            x = self.dmx['x']*255
            y = self.dmx['y']*255
        return x,y


    def set_position(self, dmx):
        if 'x-coarse' in self.dmx:
            self.dmx['x-coarse']    = int(self.x/255)
            self.dmx['x-fine']      = int(self.x % 255)
            self.dmx['y-coarse']    = int(self.y/255)
            self.dmx['y-fine']      = int(self.y % 255)
        elif 'x' in self.dmx:
            self.dmx['x'] = int(self.x/255)
            self.dmx['y'] = int(self.y/255)
        return self.update(dmx)

    def off(self, dmx):
        for i in ['intensity', 
                  'color',
                  'red','green','blue','white']:
            if i in self.dmx:
                self.dmx[i] = 0
        return self.update(dmx)

    def on(self, dmx, color='white'):
        if 'intensity' in self.dmx:
            self.dmx['intensity'] = 255
            
        if 'color' in self.dmx and color in self.color_values:
            self.dmx['color'] = self.color_values[color]
        
        if color == 'white' and 'white' in self.dmx:
            self.dmx['white'] = 255
        
        if ((color == 'white' or color == 'red') and
            'red' in self.dmx):
            self.dmx['red']= 255
        if ((color == 'white' or color == 'green') and
            'red' in self.dmx):
            self.dmx['green']= 255
        if ((color == 'white' or color == 'blue') and
            'red' in self.dmx):
            self.dmx['blue']= 255
        return self.update(dmx)


class Show:
    def __init__(self, config, name):
        self.data = config.shows[name]
        self.fixture_groups=self.data['fixture_groups']
        self.fixtures = self.data['fixtures']

        for fname in self.fixtures:
            fixture = self.fixtures[fname]
            type = fixture['type']
            if type in config.fixture_profiles:
                fixture['profile'] = config.fixture_profiles[type]
