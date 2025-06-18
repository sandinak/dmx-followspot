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
import sys
import yaml
import glob
import logging as log
CONFIG_FILE = 'dmxfs.yml'


class DMXInput:
    def __init__(self, data):
        self.data = data
        self.universe = self.data['universe']
        self.id = self.data['id']


class DMXOutput:
    def __init__(self, data):
        self.data = data
        self.universe = self.data['universe']


class DFSConfig:
    def __init__(self, path='config/%s' % CONFIG_FILE):
        log.info('reading config from %s' % path)
        if not os.path.exists(path):
            print('missing %s, cannot run.' % path)
            sys.exit(1)
        with open(path, 'r') as stream:
            self.config = yaml.load(stream, Loader=yaml.FullLoader)

        self.fixture_profiles = self.load_fixture_profiles()

        self.dmx = self.config['dmx']
        self.input = DMXInput(self.config['dmx']['input'])
        self.output = DMXOutput(self.config['dmx']['output'])
        self.joystick = self.config['joystick']

    def load_fixture_profiles(self, path='config/fixture_profiles'):
        ''' 
        read in each .yml file in the directory as a set of 
        fixtures.
        '''
        # TODO: recurse directories here?
        all_fixtures = dict()
        if not os.path.exists(path):
            print('missing %s, cannot run.' % path)
            sys.exit(1)
        for f in glob.glob('%s/*.yml' % path):
            log.info('reading %s' % f)
            with open(f, 'r') as stream:
                try:
                    fixtures = yaml.load(stream, Loader=yaml.FullLoader)
                except (yaml.yamlError, yaml.MarkedYamlError) as e:
                    log.error(
                        'cannot read %s : YAML error: %s' % (
                            f,
                            str(e)))
            for k, v in fixtures.items():
                log.info('  loading fixture %s' % k)
                all_fixtures[k] = v
        return all_fixtures
