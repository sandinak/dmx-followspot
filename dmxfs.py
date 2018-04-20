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

from __future__ import print_function

import argparse
import array
import atexit
import io
import os
import pprint
import signal
import sys
import textwrap

from ola.ClientWrapper import ClientWrapper
import yaml

sys.path.append('lib')
from config import DFSConfig
from handler import DmxHandler
import logging as log
from show import Show
from stage import Stage
import xbox


__author__ = 'branson@sandsite.org'


def killall():
    ''' cleanup subprocesses .. needed for joystick'''
    os.killpg(os.getpgrp(), signal.SIGHUP)


def setup_logging(args):
    '''setup global logging and send a start entry'''
    global debug, verbose
    if args.debug:
        log.basicConfig(
            format="%(levelname)s: %(message)s",
            level=log.DEBUG)
        log.debug("Debugging enabled.")
        debug = True
    elif args.verbose:
        log.basicConfig(
            format="%(levelname)s: %(message)s",
            level=log.INFO)
        log.info("Verbose output.")
        verbose = True
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")


def parse_args():
    ''' 
    read in command-line arguments 
    '''
    parser = argparse.ArgumentParser(
        description="DMX Followspot")
    # defaults
    parser.set_defaults(verbose=False)
    parser.set_defaults(show_errors=False)
    parser.set_defaults(check_mode=False)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Set verbose output.")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Show debugging output.")
    parser.add_argument("-c", "--check-mode", action="store_true",
                        help="check config files for readability")

    parser.add_argument("-l", "--stage-name",
                        default='default',
                        help="load configured location")

    parser.add_argument("-s", "--show-name",
                        default='default',
                        help="load specific show")
    return parser.parse_args()


def main():
    atexit.register(killall)
    args = parse_args()
    setup_logging(args)
    # read tool config
    config = DFSConfig()

    # setup show
    show = Show(config, args.show_name)
    if not show:
        print('no such show %s', args.show_name)
        sys.exit(1)

    # setup stage
    stage = Stage(show, args.stage_name)
    if not stage:
        print('could not load or create stage %s', args.stage_name)
        sys.exit(1)

    # setup joystick
    joy = xbox.Joystick()

    if args.check_mode:
        sys.exit(0)

    handler = DmxHandler(config, show, stage, joy)

    # setup data handler, this is our callback loop
    # as DMX data comes in constantly
    wrapper = ClientWrapper()
    rx = wrapper.Client()
    rx.RegisterUniverse(
        config.input.universe,
        rx.REGISTER,
        handler.handle)
    wrapper.Run()


if __name__ == "__main__":
    main()
