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
CONFIG_FILE='config.yml'

''' DMX input and output config '''
class DMXInput:
    def __init__(self,data):
        self.data = data
        self.universe = self.data['universe']
        self.id = self.data['id']


class DMXOutput:
    def __init__(self,data):
        self.data=data
        self.universe = self.data['universe']


class DFSConfig:
    def __init__(self, path=CONFIG_FILE):
        if not os.path.exists(path):
            print('missing %s, cannot run.' % path)
            sys.exit(1)
        with open(path, 'r') as stream:
            self.config = yaml.load(stream)

        self.shows = self.config['shows']
        self.fixture_profiles = self.config['fixture_profiles']
        self.dmx = self.config['dmx']
        self.input = DMXInput(self.config['dmx']['input'])
        self.output = DMXOutput(self.config['dmx']['output'])
        
    def show(self, name):
        if name in self.shows:
            Show(self.shows[name], self.fixture_profiles)
            
    def fixture_profile(self, name):
        if name in self.fixture_profiles:
            self.fixture_profiles[name]

