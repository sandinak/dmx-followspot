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
import numpy as np
import vectors as v
import math
import os
import yaml
import pprint

SCENE_FILE='scenes.yml'
# matches 
SCENE_COUNT=255

def angle_between(p1, p2):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return np.rad2deg((ang1 - ang2) % (2 * np.pi))

def distance_between(p1, p2):
    return math.sqrt((p1[1] - p1[0])**2 + (p2[1] - p2[0])**2)

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class Show:
    def __init__(self, config, name):
        self.data = config.shows[name]
        self.fixture_aspects = config.fixture_aspects
        self.fixture_groups=self.data['fixture_groups']
        self.fixtures = self.data['fixtures']

        for fname in self.fixtures:
            fixture = self.fixtures[fname]
            type = fixture['type']
            aspect = fixture['aspect']
            if type in config.fixture_profiles:
                fixture['profile'] = config.fixture_profiles[type]
            if aspect in config.fixture_aspects:
                fixture['aspect'] = config.fixture_aspects[aspect]


class Scene:
    def __init__(self, scene_id, config, path=SCENE_FILE):
        if not os.path.exists():
            print('missing %s, cannot run.' % path)
            sys.exit(1)
        with open(path, 'r') as stream:
            self.data = yaml.load(stream)
        self.scene = self.data[scene_id]
        self.fixturegroup = self.scene['fixture_group']
        self.x =  self.scene['x']
        self.x =  self.scene['y']
        self.x =  self.scene['z']
    
        


                
class Target:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class FixtureGroup:
    def __init__(self, fixtures):
        self.fixtures = fixtures
        
        
    def point(self, target):
        for f in fixtures:
            f.point_to(target)

class Fixture:
    def __init__(self, show, name):
        self.show = show
        self.name = name
        self.data = self.show.fixtures[self.name]
        self.type = self.data['type']
        self.id = self.data['id']
        self.profile = self.data['profile']

        # we can't set up degree per step because we don't know
        # if we're in 8-bit or 16-bit mode
        self.h_range = self.profile['h-range']
        self.v_range = self.profile['v-range']

        # setup aspect of the fixture
        self.aspect = self.data['aspect']
        if 'hx' in self.profile:
            self.hx = self.profile['hx']
            self.vz = self.profile['vz']
        else: 
            self.hx = self.aspect['hx']
            self.vz = self.aspect['vz']

        # setup x and z axis so we know where to go
        # this is relative to the most significant DMX value for H and V 
        self.h_x_axis = (self.hx * 255)
        self.v_z_axis = (self.vz * 255)
        
        log.debug('%s setting h_x_axis: %f from %f' % (self.name, self.h_x_axis,self.hx))

        # setup rotation and 
        self.h_rotation = -1
        if (('h-rotation' in self.profile and self.profile['h-rotation'] == 'cw') or
            (self.aspect and 'h-rotation' in self.aspect and self.aspect['h-rotation'] == 'cw')):
            self.h_rotation = 1

        self.v_rotation = -1
        if (('v-rotation' in self.profile and self.profile['v-rotation'] == 'cw') or
            (self.aspect and 'v-rotation' in self.aspect and self.aspect['v-rotation'] == 'cw')):
            self.v_rotation = 1
#        else: 
            # TODO: add for inverted install

        self.channels = self.profile['channels']
        self.managed_attributes = self.profile['managed_attributes']
        
        # location
        self.x = self.data['x'] if 'x' in self.data else None
        self.y = self.data['y'] if 'y' in self.data else None
        self.z = self.data['z'] if 'z' in self.data else None

        # dmx control 
        # we abstract this to make it quicker to store 8 and 16 bit
        self.h = (255*255)/2
        self.v = (255*255)/2
        self.cfocus = self.data['focus'] if 'focus' in self.data else 0
        # our stored data 
        self.dmx = dict()

        if 'color_values' in self.profile:
            self.color_values = self.profile['color_values']

        # init map values
        for c in self.channels:
            self.dmx[c] = 0
            
    def located(self):
        if (self.x is not None and 
            self.y is not None and 
            self.z is not None):
            return True

    def location(self):
        return (self.x, self.y, self.z)
            
    def point_to(self, target):
        log.debug('pointing %s at %s which rotates %d ' % (
                self.name, target.name, self.h_rotation ))
        # determine target vector
        pa = v.Point(self.x, self.y, self.z)
        pb = v.Point(target.x, target.y, target.z)
        vt = v.Vector.from_points(pa, pb)
        # determine this fixtures settings
        # H .. relative to x axis
        px = v.Point(self.x+1, self.y, 0)
        vx = v.Vector.from_points(pa, px) 
        # absolute angle
        ha = vt.angle(vx) 
        # compute based on rotation
        if ( self.h_rotation == -1 and target.x < self.x ):
            # CCW
#            log.debug('  ccw adding 180 %f to %f ' % (ha, 360-ha))
            ha = 360 - ha

        elif ( self.h_rotation == 1 and target.x > self.x ):
            # CW
#            log.debug('  cw adding 180 %f to %f ' % (ha, 360-ha))
            ha = 360 - ha

        # V ... relative to straight vector - height
        pz = v.Point(target.x, target.y, self.z)
        vz = v.Vector.from_points(pa, pz)
        va = vt.angle(vz)

#        log.debug('  s: %d, %d t: %d, %d ha: %d, va: %d' % ( 
#            self.x, self.y, target.x, target.y, ha, va))

        self.set_angles(ha, va)


    def set_angles(self, hd ,vd):
        self.h = (
            self.h_x_axis + ((hd * 65535) / self.h_range) 
        )
#        log.debug('  h: %f + %f = %f ' % (
#            self.h_x_axis/255,
#            (hd*65535/self.h_range)/255,
#            self.h/255))
        self.v = (
            self.v_z_axis + ((vd * 65535)/ self.v_range)
        )
        self.set_coordinates()


    def set_coordinates(self):
        if 'h-coarse' in self.dmx:
            self.dmx['h-coarse']    = int(self.h/255)
            self.dmx['h-fine']      = int(self.h % 255)
            self.dmx['v-coarse']    = int(self.v/255)
            self.dmx['v-fine']      = int(self.v % 255)
            log.debug('%s  8-bit %f,%f' % (self.name, 
                                    self.dmx['h-coarse'], 
                                    self.dmx['v-coarse']))
        elif 'h' in self.dmx:
            self.dmx['h'] = int(self.h/255)
            self.dmx['v'] = int(self.v/255)

    def update_dmx(self, dmx):
        for c in self.channels:
            dmx_i = self.id + self.channels.index(c) - 1
            dmx[dmx_i] = clamp(self.dmx[c], 0, 255)
        return dmx
        
    def get_position(self, dmx):
        if 'x-coarse' in self.dmx:
            x = ((self.dmx['x-coarse'] * 255) + self.dmx['x-fine'])
            y = ((self.dmx['y-coarse'] * 255) + self.dmx['y-fine'])
        else: 
            x = self.dmx['x']*255
            y = self.dmx['y']*255
        return x,y
    
    def update_focus(self, value):
        if 'focus' in self.dmx:
            self.dmx['focus'] = clamp(self.dmx['focus']+value, 0 , 255)

    def update_coordinates(self, mod_h, mod_v ):
#        if mod_h or mod_v:
#            log.debug('moving %s by %d, %d' % (self.name, mod_h, mod_v))
        self.h = clamp(self.h + mod_h, 0, 65535)
        self.v = clamp(self.v + mod_v, 0, 65535)
        self.set_coordinates()


    def get_angles(self):
        return ( self.h /(255*255) * self.h_range,
                 self.v /(255*255) * self.v_range)

    def off(self):
        for i in ['intensity', 
                  'color',
                  'red','green','blue','white']:
            if i in self.dmx:
                self.dmx[i] = 0


    def on(self, color='white'):
        if 'intensity' in self.dmx:
            self.dmx['intensity'] = 255
            
        if 'shutter' in self.dmx:
            self.dmx['shutter'] = 255 
            
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


