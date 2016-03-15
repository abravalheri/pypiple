#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automated tests for pypiple.index.Index#diff
"""
import os

from pypiple.index import Index

__author__ = 'Anderson Bravalheri'
__copyright__ = 'Anderson Bravalheri'
__license__ = 'Mozilla Public License Version 2.0'


def test_diff_list_removed_packages(
    package_dir, package_files, index_with_fake_retrieve):
    """
    diff should recognize removed ``packages``
    """
    index = index_with_fake_retrieve(package_dir)
    index.update()

    remove_file = os.path.join(package_dir, package_files[0])
    os.remove(remove_file)

    added, dirty, removed = index.diff(index.scan())

    assert added == set()
    assert dirty == set()
    assert removed == set([remove_file])