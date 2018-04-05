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

import os
import yaml
import pprint

STORED_FILE='data.yml'

class State:
    def __init__(self, path=STORED_FILE):
        self.read()


    def read(self):
        if os.path.exists(path):
            log.info('reading %s' % path)
            with open(path, 'r') as stream:
                self.state = yaml.load(stream)
        else:
            self.state = State()
            self.shows = self.state['shows']


    def write(self):
         with open(path, 'w') as yaml_file:
             yaml.dump(self.state, yaml_file, default_flow_style=False)


class Location:
    def __init__(self,name):
        self.name = name
        

class SceneState(State):
    def __init__(self,scene):
        self.data=scene
        
class FGState(State):
    def __init__(self,fg):
        self.fg=fg
