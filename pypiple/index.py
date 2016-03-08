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
from os.path import getmtime, isfile, join, splitext

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
""".. PKG_FIELDS_:

list of metadata to be retrieved from pakage
"""

PKGINFO_CLASSES = {
    'whl': pkginfo.Wheel,
    'egg': pkginfo.BDist,
    'tar.gz': pkginfo.SDist,
}


def filter_info(info):
    """Filter most relevant information about package.
    
    Returns:
        A dict with PKG_FIELDS_ key.
    """
    filtered = {field: getattr(info, field) for field in PKG_FIELDS}

    if not info.maintainer:
        filtered['maintainer'] = info.author
        filtered['maintainer_email'] = info.author_email

    return filtered


def retrieve_data(path):
    """Retrieve metadata about the python package.

    Returns:
        A dict with PKG_FIELDS_ key.
    """

    base, ext = splitext(path)
    info = PKGINFO_CLASSES[ext](path)
    return filter_info(info)


#def find_packages_by_ext(path, ext):
#    decoder = PKGINFO_CLASSES[ext]
#    files = glob(join(path, '*.{}'.format(ext)))
#    return [decoder(file_path) for file_path in files]


#def find_packages(path):
#    pkgs = [find_packages_by_ext(path, ext) for ext in PKGINFO_CLASSES.keys()]
#    return concatenate(pkgs)


#def get_name(pkg):
#    return pkg["name"]


def compare_versions(pkg1, pkg2):
    return semver.compare(pkg1['version'], pkg2['version'])


class Index(object):
    """docstring for Index

    .. _support:

    Note:
        The following package formats are supported:

        ``*.whl`` - binary packages created with ``setup.py bdist_wheel``
        ``*.egg`` - binary packages created with ``setup.py bdist_egg``
        ``*.tar.gz`` - source packages created with ``setup.py sdist``

        Package format is deduced from file extension.
    """

    def __init__(self, path):
        super(Index, self).__init__()
        self.path = path
        self._cache = {
            'mtime': None,  # => last index update
            'lookup': {},  # => primary source of true
            'packages': {},  # => groupedby name
        }


    def uptodate(self):
        """Discover if the index cache is uptodate.

        Returns:
            True if no change in index directory since the last update
        """
        mtime = self.mtime()

        return mtime and mtime >= getmtime(self.path)


    def mtime(self, pkg=None):
        """Retrieve the time instant when the index where updated.

        Keyword Arguments:
            pkg (string): path to a package. When given, this method will
            return the mtime of the file, read during the last update.
            Default is None.

        Returns:
            Time instant for the last update in index, or the cached mtime
            value for a specified package.
        """
        if pkg:
            return self._cache['lookup'][pkg]['mtime']

        return self._cache['mtime']


    def scan(self):
        """Scan the index directory searching for python packages.

        See support_.

        Returns:
            List of paths for package files inside index directory.
        """
        types = PKGINFO_CLASSES.keys()
        pkgs = [glob(join(path, '*.{}'.format(ext))) for ext in types]
        return concatenate(pkgs)


    def diff(self, pkgs):
        """Compute the difference between index cache and the given list
        of paths for packages.

        Arguments:
            pks (List[str]): List of paths pointing to python packages

        Returns:
            Tuple with 3 elements.
            The first element is a list of packages present in the given list
            but absent in the index cache.
            The second element is a list of packages present in both, but
            have been modified.
            The last element is a list of packages absent in the given list,
            but present in the index cache.
        """
        cached = set(self._cache['lookup'].keys())
        current = set(pkgs)

        added = current - cached
        removed = cached - current
        suspects = current & cached  # intersection
        dirty = [pkg for pkg in suspects if getmtime(pkg) > self.mtime(pkg)]

        return (added, dirty, removed)


    def update(self):
        if self.uptodate():
            return ([], [])

        current = self.scan()
        (added, dirty, removed) = self.diff(current)

        for path in removed:
            del self._cache['lookup'][path]

        modified = added + dirty
        self._cache['lookup'].update({
            path: retrieve_data(path) for path in modified})

        # Expire cache
        self._cache['packages'] = []

        return (modified, removed)


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
