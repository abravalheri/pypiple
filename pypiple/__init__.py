#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple and customizable Python Package Index
"""
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:  # pylint: disable=bare-except
    __version__ = 'unknown'
