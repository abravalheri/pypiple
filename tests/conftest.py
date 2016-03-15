#!/usr/bin/env python
# -*- coding: utf-8 -*-

# isort:skip_file

"""
    Dummy conftest.py for pypiple.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""
from __future__ import print_function, absolute_import, division

import os

import pytest


def filename(pkg):
    """Build file name for pkg"""

    return '{}-{}.{}'.format(pkg['name'], pkg['version'], pkg['ext'])


@pytest.fixture()
def extra_files():
    """Dummy files"""

    return ['some-file.txt', 'the-file.c', 'other-file.py', '1moar-file.json']


@pytest.fixture()
def packages():
    """Dummy package metadata"""

    return [
        {'name': 'some-pkg', 'version': '3.0.0', 'ext': 'whl'},
        {'name': 'some-pkg', 'version': '2.0.0', 'ext': 'egg'},
        {'name': 'some-pkg', 'version': '1.0.0', 'ext': 'tar.gz'},
        {'name': 'the-pkg', 'version': '0.2.0', 'ext': 'whl'},
        {'name': 'the-pkg', 'version': '0.1.0', 'ext': 'egg'},
        {'name': 'other-pkg', 'version': '0.0.0-alpha', 'ext': 'tar.gz'},
    ]


@pytest.fixture()
def package_files(packages):
    """Dummy package files"""

    return [filename(pkg) for pkg in packages]


@pytest.fixture()
def package_dir(tmpdir, package_files, extra_files):
    """Sample directory populated with dummy eggs, wheels, tgzs and others"""

    dirpath = str(tmpdir)

    # populate dir with dummies
    for name in package_files + extra_files:
        with open(os.path.join(dirpath, name), 'w'):  # touch file
            pass

    return dirpath


def retrieve_data(path, packages):
    """Retrieve metadata about the dummy package.

    Returns:
        A dict with all keys in PKG_FIELDS_.
    """
    try:
        basename = os.path.basename(path)
        data = [pkg for pkg in packages if filename(pkg) == basename][0].copy()
        data['mtime'] = os.path.getmtime(path)
        return data
    except (RuntimeError, ValueError, KeyError):
        LOGGER.error('Unnable to read information about %s', basename(path))


@pytest.fixture()
def index_with_fake_retrieve(monkeypatch, packages):
  """Version of Index monkeypatched to not use pkginfo"""

  fake = lambda path: retrieve_data(path, packages)
  monkeypatch.setattr('pypiple.index.retrieve_data', fake)
  import pypiple.index

  return pypiple.index.Index