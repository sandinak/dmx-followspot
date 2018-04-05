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
# fixtures.py
# Copyright (C) 2018 Branson Matheson   

class FixtureLocations:
    def __init__(self,data=dict()):
        self.data = data

    def load(self,name):
        if name in self.data:
            self.data[name] 


class FixtureLocation(FixtureLocations):
 def __init__(self, name, **kwargs):
        fixturelocation = super().load(name)
        if fixturelocation:
            self.data = fixturelocation
        else: 
            self.data.name = name
        for k,v in kwargs.iteritems():
            self.data.k = v