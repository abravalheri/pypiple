#!/usr/bin/env python
# -*- coding: utf-8 -*-

# isort:skip_file
# pylint: disable=redefined-outer-name

"""
    Dummy conftest.py for pypiple.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""
from __future__ import print_function, absolute_import, division

import os
from time import time

import pytest

from pypiple.index import Index


def filename(pkg):
    """Build file name for pkg"""

    return '{}-{}.{}'.format(pkg['name'], pkg['version'], pkg['ext'])


@pytest.fixture()
def extra_files():
    """Dummy files"""

    return ['some-file.txt', 'the-file.c', 'other-file.py', '1moar-file.json']


@pytest.fixture()
def package_data():
    """Dummy package metadata"""

    pkgs = [
        {'name': 'some-pkg', 'version': '3.0.0', 'ext': 'whl'},
        {'name': 'some-pkg', 'version': '2.0.0', 'ext': 'egg'},
        {'name': 'some-pkg', 'version': '1.0.0', 'ext': 'tar.gz'},
        {'name': 'the-pkg', 'version': '0.2.0', 'ext': 'whl'},
        {'name': 'the-pkg', 'version': '0.1.0', 'ext': 'egg'},
        {'name': 'other-pkg', 'version': '0.0.0-alpha', 'ext': 'tar.gz'},
    ]

    mtime = {'mtime': time()}

    return [pkg.update(mtime) or pkg for pkg in pkgs]  # dict merge


@pytest.fixture()
def package_files(package_data):
    """Dummy package files"""

    return [filename(pkg) for pkg in package_data]


@pytest.fixture()
def package_dir(tmpdir, package_files, extra_files):
    """Sample directory populated with dummy eggs, wheels, tgzs and others"""

    dirpath = str(tmpdir)

    # populate dir with dummies
    for name in package_files + extra_files:
        with open(os.path.join(dirpath, name), 'w'):  # touch file
            pass

    return dirpath


@pytest.fixture()
def package_paths(package_dir, package_files):
    """Paths to dummy packages"""

    return [os.path.join(package_dir, pkg) for pkg in package_files]


@pytest.fixture()
def index(package_dir, package_data, package_paths):
    """
    Dummy package index, pre-initialized
    """

    pkg_index = Index(package_dir)
    # monkeypatch cached properties to avoid system calls
    pkg_index.__dict__['files'] = package_paths
    pkg_index.__dict__['metadata'] = dict(zip(package_paths, package_data))

    return pkg_index
