import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from unittest.mock import MagicMock

class MockModule(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()

    __name__ = 'mock'
    __loader__ = None
    __spec__ = None
    __path__ = []
    __file__ = None
    __package__ = 'mock'

MOCK_MODULES = [
    'pyb',
    'micropython',
    'utime',
    'ulab',
    'ulab.numpy',
    'cotask',
    'task_share',
    'bumpsensor',
    'linesensor',
    'motor_driver',
    'encoder',
    'imu_driver',
]

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = MockModule()

import time
time.ticks_us = MagicMock()
time.ticks_diff = MagicMock()
time.ticks_ms = MagicMock()

project = 'ME405 Term Project'
copyright = '2026, Ethan Dickson, Kaitlyn Ould'
author = 'Ethan Dickson, Kaitlyn Ould'
release = '1.0'

extensions = ['sphinx.ext.autodoc']

autoclass_content = "both"

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']