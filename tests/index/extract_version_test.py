#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automated tests for pypiple.index.extract_version

Objective:
    Guarantee extracted versions ignore build metadata and
    can be properly sorted
"""
from itertools import permutations

import pytest

from pypiple.index import extract_version

__author__ = 'Anderson Bravalheri'
__copyright__ = 'Anderson Bravalheri'
__license__ = 'Mozilla Public License Version 2.0'


def test_extract_version_ignore_build():
    """
    extract_version should ignore build metadata
    pkgs that diff just for build metadata should have
    the same sorting precedence
    """
    pkg1 = {'version': '1.0.0-beta+20130313144700'}
    pkg2 = {'version': '1.0.0-beta+exp.sha.5114f85'}

    version1 = extract_version(pkg1)
    version2 = extract_version(pkg2)

    assert version1 == version2
    assert '20130313144700' not in version1
    assert 'exp.sha.5114f85' not in version2
    assert version1[0] == '1'
    assert version1[1] == '0'
    assert version1[2] == '0'
    assert version1[3] == 'beta'

    pkgs = [pkg1, pkg2]
    assert sorted(pkgs, key=extract_version) == pkgs

    pkgs = [pkg2, pkg1]
    assert sorted(pkgs, key=extract_version) == pkgs


@pytest.mark.slow
def test_extract_version_produce_sortables():
    """
    extract_version should produce sortable objects
    The sorting order is: major > minor > patch > release-type
    release-types: rc > beta > alpha
    """
    versions = [
        # major > minor > patch
        '4.1.0', '3.3.0', '3.2.3',
        # patch > release
        '2.1.2', '2.1.1-alpha', '2.1.0-rc',
        # rc > beta > alpha
        '1.2.0-rc', '1.2.0-beta', '1.2.0-alpha',
    ]

    pkg_list = [{'version': version} for version in versions]

    for pkgs in permutations(pkg_list):
        assert sorted(pkgs, key=extract_version, reverse=True) == pkg_list
