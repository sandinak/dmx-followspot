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
import time

SCENE_FILE='scenes.yml'
# matches 
SCENE_COUNT=255


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


''' an object that defines all fixtures used in an environment'''
class Show:
    def __init__(self, config, name):
        self.data = config.shows[name]
        self.fixture_aspects = config.fixture_aspects
        self.fixture_groups=self.data['fixture_groups']
        self.fixtures = self.data['fixtures']
        self.fixture_group_names = sorted(self.fixture_groups.iterkeys())

        for fname in self.fixtures:
            fixture = self.fixtures[fname]
            type = fixture['type']
            aspect = fixture['aspect']
            if type in config.fixture_profiles:
                fixture['profile'] = config.fixture_profiles[type]
            if aspect in config.fixture_aspects:
                fixture['aspect'] = config.fixture_aspects[aspect]

''' a stored object that defines a fixture group and starting location'''
class Scene:
    def __init__(self, show, scene_id, path=SCENE_FILE):
        self.show = show
        self.scene_id = scene_id
        self.path = path

        if not os.path.exists(path):
            print('missing %s, cannot run.' % path)
            sys.exit(1)
        with open(path, 'r') as stream:
            self.data = yaml.load(stream)
        self.speed = 40
        self.deadzone = 6000
        self.scene = self.data[scene_id]
        self.edit_mode = 0
        self.all_lights = False
        self.name = self.scene['name']
        self.fixture_group = FixtureGroup(self.show, self.scene['fixture_group'])
        self.target = Target(
            self.name, 
            self.scene['x'], 
            self.scene['y'], 
            self.scene['z'])
        self.fixture_group.point_to(self.target)

    def save(self, path=SCENE_FILE):
        if not os.path.exists(path):
            print('missing %s, cannot save.' % path)
        with open(path, 'r') as stream:
            data = yaml.load(stream)
        data[self.scene_id] = self.scene
        data[self.scene_id]['x'] = self.target.x
        data[self.scene_id]['y'] = self.target.y
        data[self.scene_id]['z'] = self.target.z

        with open(path, 'w') as stream:
            yaml.dump(data, stream, default_flow_style=False)

    ''' take input and modify position'''
    def run(self, joy, dmx):
        if not edit_mode and joy.Start():
            edit_mode = 1
        elif edit_mode and joy.Start():
            edit_mode = 0
        
        if edit_mode:
            dmx=handle_commands(joy.dmx)

        dmx=self.handle_movement(joy,dmx)
        return dmx
        
    def edit(self,joy,dmx):
        dmx=self.handle_commands(joy, dmx)
        dmx=self.handle_lights(joy, dmx)
        dmx=self.handle_movement(joy, dmx)
        return self.fixture_group.update_dmx(dmx)
        
    def handle_commands(self, joy, dmx):
        if joy.B():
            log.info('saving scene %d' % self.scene_id )
            self.save()
        elif joy.rightBumper():
            self.fixture_group.lights_off()
            self.fixture_group = FixtureGroup(
                self.show, 
                self.show.fixture_group_names[
                    (self.show.fixture_group_names.index(self.fixture_group.name) + 1) % 
                    len(self.show.fixture_group_names)
                    ]
                )
            self.fixture_group.point_to(self.target)
        elif joy.leftBumper():
            self.fixture_group.lights_off()
            self.fixture_group = FixtureGroup(
                self.show, 
                self.show.fixture_group_names[
                    (self.show.fixture_group_names.index(self.fixture_group.name) - 1) % 
                    len(self.show.fixture_group_names)
                    ]
                )
            self.fixture_group.point_to(self.target)
            
        return dmx

    def handle_movement(self, joy, dmx):
        if joy.dpadUp():
            self.speed = clamp(self.speed+5, 2, 100)
            log.debug(' speed: %d' % self.speed)
            time.sleep(0.2)
        elif joy.dpadDown():
            self.speed = clamp(self.speed-5, 2, 100)
            log.debug(' speed: %d' % self.speed)
            time.sleep(0.2)
        # handle movement
        rx = joy.rightX(self.deadzone)
        ry = joy.rightY(self.deadzone)
        if rx or ry:
            self.target.x += self.speed * rx/100
            self.target.y += self.speed * ry/100
            log.debug('target: %f, %f' % (self.target.x, self.target.y))
            self.fixture_group.point_to(self.target)
        return dmx
    
    def handle_lights(self, joy, dmx):
        # handle light 
        if self.all_lights ==  False and joy.rightTrigger():
            self.all_lights = True
            self.fixture_group.lights_on()
            log.debug('all_on')
            time.sleep(0.2)
            return self.fixture_group.update_dmx(dmx)
        elif self.all_lights == True and joy.rightTrigger():
            self.all_lights = False
            self.fixture_group.lights_off()
            log.debug('all_off')
            time.sleep(0.2)
            return self.fixture_group.update_dmx(dmx)
        return dmx


''' things on the stage we point to'''
class Target:
    def __init__(self, name, x, y, z):
        self.name = name
        self.x = x
        self.y = y
        self.z = z

''' groups of fixtures we modify as part of the run operation'''
class FixtureGroup:
    def __init__(self, show, name):
        self.show = show
        self.name = name
        self.fixtures = dict()
        for f in show.fixture_groups[name]:
            self.fixtures[f] = Fixture(show, f)

    def point_to(self, target):
        for f in self.fixtures:
            self.fixtures[f].point_to(target)

    def update_dmx(self, dmx):
        for f in self.fixtures:
            dmx = self.fixtures[f].update_dmx(dmx)
        return dmx

    def lights_on(self):
        for f in self.fixtures:
            self.fixtures[f].on()

    def lights_off(self):
        for f in self.fixtures:
            self.fixtures[f].off()

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
        
        log.debug('%s h_x_axis: %f' % (self.name, self.h_x_axis))

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
        # determine target vector
        pa = v.Point(self.x, self.y, self.z)
        pb = v.Point(target.x, target.y, target.z)
        vt = v.Vector.from_points(pa, pb)
        # determine this fixtures settings
        # H .. relative to x axis
        px = v.Point(self.x+100, self.y, 0)
        vx = v.Vector.from_points(pa, px) 
        # absolute angle
        ha = vx.angle(vt) 

        # fip angle if we pass the y axis
        if ( self.h_rotation == -1 and target.y < self.y ):
            ha = 360 - ha

        elif ( self.h_rotation == 1 and target.y < self.y ):
            log.debug('reverse %f to %f' % (ha, 360-ha))
            ha = 360 - ha

        # V ... relative to straight vector - height
        pz = v.Point(target.x, target.y, self.z)
        vz = v.Vector.from_points(pa, pz)
        if target.z <= 0: 
            va = 0 
        else: 
            va = vt.angle(vz)
        self.set_angles(ha, va, target)


    def set_angles(self, ha ,va, target):
        self.h = (
            self.h_x_axis + ((ha * 65535) / self.h_range) * (self.h_rotation*-1)
        )
        self.v = (
            self.v_z_axis + ((va * 65535)/ self.v_range) 
        )
        log.debug('%s s: %f,%f t: %f,%f ha: %f h0: %f va: %f v0: %f f: %f, %f' % (
            self.name, 
            self.x, self.y, 
            target.x, target.y, 
            ha, self.h_x_axis/255,
            va, self.v_z_axis/255,
            self.h/255, self.v/255))
        self.set_coordinates()


    def set_coordinates(self):
        if 'h-coarse' in self.dmx:
            self.dmx['h-coarse']    = int(self.h/255)
            self.dmx['h-fine']      = int(self.h % 255)
            self.dmx['v-coarse']    = int(self.v/255)
            self.dmx['v-fine']      = int(self.v % 255)
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


