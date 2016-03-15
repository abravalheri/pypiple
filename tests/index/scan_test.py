#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automated tests for pypiple.index.Index#scan
"""
import os

from pypiple.index import Index

__author__ = 'Anderson Bravalheri'
__copyright__ = 'Anderson Bravalheri'
__license__ = 'Mozilla Public License Version 2.0'


def test_scan_list_packages(package_dir, package_files):
    """
    scan should return a list containing all ``.egg``s,  ``.whl``s
    and ``.tar.gz``s inside directory
    """

    expected = [
        os.path.join(package_dir, pkg)
        for pkg in package_files
    ]

    index = Index(package_dir)
    pkgs = index.scan()

    for name in expected:
        assert name in pkgs


def test_scan_not_list_extra_files(package_dir, extra_files):
    """
    scan should return a list that do not contain anything but
    ``.egg``s,  ``.whl``s and ``.tar.gz``s
    """

    index = Index(package_dir)
    pkgs = index.scan()

    for pkg in pkgs:
        assert any(ext in pkg for ext in ('egg', 'whl', 'tar.gz'))

    not_expected = [
        os.path.join(package_dir, name)
        for name in extra_files
    ]

    for name in not_expected:
        assert name not in pkgs
