#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Automated tests for pypiple.index.Index#packages
"""

import pytest

__author__ = 'Anderson Bravalheri'
__copyright__ = 'Anderson Bravalheri'
__license__ = 'Mozilla Public License Version 2.0'


@pytest.fixture()
def small_index(index):
    """Package index with 1 package x 3 versions"""
    pkgs = {
        '/path/pkg2-2.0.0': {
            'name': 'some-pkg', 'version': '2.0.0', 'ext': 'egg'
        },
        'path/pkg3-1.0.0': {
            'name': 'some-pkg', 'version': '1.0.0', 'ext': 'tar.gz'
        },
        './path/pkg1-3.0.0': {
            'name': 'some-pkg', 'version': '3.0.0', 'ext': 'whl'
        },
    }

    # monkey patch
    index.__dict__['files'] = pkgs.keys()
    index.__dict__['metadata'] = pkgs

    return index


def test_packages_indexed_by_plain_name(index):
    """packages should be a dict, indexed by plain pkg name instead of path"""

    pkgs = index.packages
    assert isinstance(pkgs, dict)
    for key, versions in pkgs.items():
        assert '.' not in key  # does not contain version
        assert '/' not in key  # is not a path
        assert isinstance(versions, list)
        assert all(pkg['name'] == key for pkg in versions)


def test_package_contain_all_versions(small_index):
    """packages should contain all versions"""

    assert len(small_index.packages) == 1
    assert len(small_index.packages['some-pkg']) == 3


def test_package_versions_are_sorted(small_index):
    """packages should contain sorted versions"""

    assert small_index.packages['some-pkg'][0]['version'] == '3.0.0'
    assert small_index.packages['some-pkg'][1]['version'] == '2.0.0'
    assert small_index.packages['some-pkg'][2]['version'] == '1.0.0'
