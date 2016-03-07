#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following line in the
entry_points section in setup.cfg:

    console_scripts =
     fibonacci = pypiple.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""
import logging
from collections import namedtuple
from glob import glob
from os.path import getmtime, isfile, join

import pkginfo
import semver

from pypiple import __version__
from pypiple.utils import concatenate

__author__ = 'Anderson Bravalheri'
__copyright__ = 'Anderson Bravalheri'
__license__ = 'Mozilla Public License Version 2.0'

PKG_FIELDS = (
    'name version summary home_page download_url maintainer maintainer_email'
).split()

PKGINFO_CLASSES = {
    'whl': pkginfo.Wheel,
    'egg': pkginfo.BDist,
    'tar.gz': pkginfo.SDist,
}


def filter_info(info):
    filtered = {field: getattr(info, field) for field in PKG_FIELDS}

    if not info.maintainer:
        filtered['maintainer'] = info.author
        filtered['maintainer_email'] = info.author_email

    return filtered


def find_packages_by_ext(path, ext):
    decoder = PKGINFO_CLASSES[ext]
    files = glob(join(path, '*.{}'.format(ext)))
    return [decoder(file_path) for file_path in files]


def find_packages(path):
    pkgs = [find_packages_by_ext(path, ext) for ext in PKGINFO_CLASSES.keys()]
    return concatenate(pkgs)


def get_name(pkg):
    return pkg["name"]


def compare_versions(pkg1, pkg2):
    return semver.compare(pkg1['version'], pkg2['version'])


class Index(object):
    """docstring for Index

    Support:
        *.whl - binary packages created with `setup.py bdist_wheel`
        *.egg - binary packages created with `setup.py bdist_egg`
        *.tar.gz - source packages created with `setup.py sdist`
    """

    def __init__(self, dirs):
        super(Index, self).__init__()
        self.dirs = list(dirs)
        self._cache = {
            'time': None,
            'by_dir': {path: [] for path in dirs},
            'list': [],
            'by_name': {},
        }

    @property
    def packages(self):
        dirs = self.dirs
        cache = self._cache

        if cache['time'] is None:
            changed = dirs
        else:
            changed = [path for path in dirs if cache['time'] < getmtime(path)]

        if changed:
            for path in changed:
                cache['by_dir'][path] = find_packages(path)

            all_pkgs = concatenate(cache['by_dir'].values())
            by_name = groupby(all_pkgs, key=lambda pkg: pkg['name'])
            by_name = {
                name: list(pkgs).sort(compare_versions)
                for name, pkgs in by_name}
            pkgs = sorted(by_name, key=get_name)

            cache['list'] = pkgs.sort(compare_versions)  # WIP
