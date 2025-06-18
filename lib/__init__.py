"""
DMX Followspot Library Package

This package contains the core modules for the DMX Followspot application:
- config: Configuration management
- handler: DMX data handling
- show: Show and scene management
- stage: Stage and fixture management
- xbox: Xbox controller interface
"""

__version__ = "1.0.0"
__author__ = "branson@sandsite.org"

# Make key classes available at package level
from .config import DFSConfig, DMXInput, DMXOutput
from .handler import DmxHandler
from .show import Show, Scene, Target, FixtureGroup, Fixture
from .stage import Stage, FixturePair

__all__ = [
    'DFSConfig', 'DMXInput', 'DMXOutput',
    'DmxHandler',
    'Show', 'Scene', 'Target', 'FixtureGroup', 'Fixture',
    'Stage', 'FixturePair',
    'xbox'
]
