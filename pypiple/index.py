#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pypiple index
-------------

Domain logic behing pypiple.

The class ``pypiple.index.Index`` is used to build a logic package index.
This index contains meta-information about all packages inside a given
directory, like file paht, author, homepage, etc and provides fast lookup
search methods. The index is also groups different versions of the same
package and is able to recognize if the cached metadata is uptodate with
the underlaying file system.

.. _PKG_FIELDS:
.. data:: PKG_FIELDS

    list of metadata to be retrieved from package

.. data:: PKG_DECODERS
    mechanism used to extract package information, according to extension
"""
import logging
from glob import glob
from itertools import groupby
from operator import add, itemgetter
from os.path import basename, getmtime, join, splitext
from time import time

import pkginfo
from property_manager import PropertyManager, cached_property
from six.moves import reduce  # noqa, pylint: disable=redefined-builtin

from pypiple import __version__  # noqa

__author__ = 'Anderson Bravalheri'
__copyright__ = 'Anderson Bravalheri'
__license__ = 'Mozilla Public License Version 2.0'

LOGGER = logging.getLogger(__name__)

PKG_FIELDS = (
    'name', 'version', 'summary', 'home_page ', 'description', 'keywords',
    'platform', 'classifiers', 'download_url', 'author', 'author_email',
    'maintainer', 'maintainer_email',
)

PKG_DECODERS = {
    'whl': pkginfo.Wheel,
    'egg': pkginfo.BDist,
    'tar.gz': pkginfo.SDist,
}


def filter_info(info):
    """Select most relevant information about package.

    Arguments:
        info (object): object with all attributes defined in PKG_FIELDS_.

    Returns:
        A dict with all keys in defined PKG_FIELDS_.
    """
    filtered = {field: getattr(info, field) for field in PKG_FIELDS}

    if not info.maintainer:
        filtered['maintainer'] = info.author
        filtered['maintainer_email'] = info.author_email

    return filtered


def retrieve_data(path):
    """Retrieve metadata about a python package.

    Arguments:
        path (string): path to the package

    Returns:
        A dict with all keys defined in PKG_FIELDS_.
    """
    try:
        _, ext = splitext(path)
        info = PKG_DECODERS[ext](path)
        data = filter_info(info)
        data['mtime'] = getmtime(path)
        return data
    except (RuntimeError, ValueError):
        LOGGER.error('Unnable to read information about %s', basename(path))


def extract_version(pkg):
    """Produce a comparable object from package version string.

    This functions assumes the package uses Semantic Versioning conventions.
    See `<http://semver.org>`_

    Arguments:
        pkg: ``dict``-like object containing package metadata.
            Required key: ``version``.

    Returns:
        tuple: components of a semantic version
    """
    relevant = pkg['version'].split('+')[0]  # ignore build info
    components = relevant.split('-')
    main = components[0]
    alias = components[1] if len(components) > 1 else ''  # e.g.: alpha, beta

    return tuple(main.split('.') + [alias])


class Index(PropertyManager):
    """Index of python packages inside a given directory path.

    This class assumes all packages are store into a single directory.
    The ``update`` method is used to sync the in-memory index with the
    current state of the storage directory.

    .. _support:

    Note:
        The following package formats are supported:

        ``*.whl`` - binary packages created with ``setup.py bdist_wheel``
        ``*.egg`` - binary packages created with ``setup.py bdist_egg``
        ``*.tar.gz`` - source packages created with ``setup.py sdist``

        Package format is deduced from file extension.
    """

    def __init__(self, path):
        """Cache-enabled index generator instance.

        After created the index is empty. In order to synchronize its contents
        with the underlaying directory, please use the method ``update``.

        Arguments:
            path (str): path to the directory used to store packages
        """
        super(Index, self).__init__()
        self.path = path
        self._mtime = None  # => last index update
        self._metadata = {}  # => primary source of true

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
            return self.metadata[pkg]['mtime']  # pylint: disable=unsubscriptable-object

        return self._mtime

    def scan(self):
        """Scan the index directory searching for python packages.

        See support_.

        Returns:
            List of paths for package files inside index directory.
        """
        types = PKG_DECODERS.keys()
        pkgs = [glob(join(self.path, '*.{}'.format(ext))) for ext in types]
        return reduce(add, pkgs)  # merge arrays

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
        cached = set(self.files)
        current = set(pkgs)

        added = current - cached
        removed = cached - current
        suspects = current & cached  # intersection
        dirty = {pkg for pkg in suspects if getmtime(pkg) > self.mtime(pkg)}

        return (added, dirty, removed)

    def update(self):
        """Update index cache based on the current state of the directory.

        Returns:
            Tuple with 2 elements.
            The first element is a list of packages modified since
            the last update.
            The second element is a list of packages removed since
            the last update.
        """
        if self.uptodate():
            return None

        current = self.scan()
        (added, dirty, removed) = self.diff(current)

        for path in removed:
            del self._metadata[path]

        modified = added | dirty  # union off sets
        self._metadata.update(
            {path: retrieve_data(path) for path in modified})
        # retrieve_data will return None if pkg decoding fails,
        # therefore, it's necessary to check null values

        # Expire cache: be lazy and regenerate it on demand
        self.clear_cached_properties()

        # Store 'last-updated' info
        self._mtime = time()

        return (modified, removed)

    @cached_property
    def files(self):
        """List of indexed files

        Lazy generated list containing all the files inside index
        directory whose type is supported.

        See support_.
        """

        return self.metadata.keys()  # pylint: disable=no-member

    @cached_property
    def metadata(self):
        """List of metadata about packages

        Lazy generated list containing all the metadata about indexed packages.
        """

        return self._metadata

    @cached_property
    def packages(self):
        """List of packages

        Lazy generated dictionary containing all different versions
        for each package, indexed by its name.
        """

        cache = self.metadata.values()  # pylint: disable=no-member
        return {
            name: sorted(infos, key=extract_version, reverse=True)
            for name, infos in groupby(cache, key=itemgetter('name'))
        }
