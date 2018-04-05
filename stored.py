 

import os
import yaml
import pprint
import logging as log

STORED_FILE='data.yml'

class Stored:
    def __init__(self, path=STORED_FILE):
        if os.path.exists(path):
            log.info('reading %s' % path)
            with open(path, 'r') as stream:
                self.data = yaml.load(stream)
        else:
            self.data = dict()
            self.data['state'] = dict()
            self.state = self.data['state']

            self.data['stages'] = dict()
            self.stages = self.data['stages']

            self.data['scenes'] = dict()
            self.scenes = self.data['scenes']
            

    def stage(self, name):
        if not name in self.stages:
            self.stages[name] = dict()
        return self.stages[name]
        

    def scene(self, name):
        if not name in self.scenes:
            self.scenes[name] = dict()
        return self.scenes[name]

    def write(self):
         with open(path, 'w') as yaml_file:
             yaml.dump(self.data, yaml_file, default_flow_style=False)

