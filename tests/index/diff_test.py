#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automated tests for pypiple.index.Index#diff
"""

from time import time

__author__ = 'Anderson Bravalheri'
__copyright__ = 'Anderson Bravalheri'
__license__ = 'Mozilla Public License Version 2.0'


def test_diff_list_removed_packages(package_paths, index):
    """
    diff should recognize removed ``packages``
    """

    # fake the removal of first package
    added, dirty, removed = index.diff(package_paths[1:])

    assert added == set()
    assert dirty == set()
    assert removed == set(package_paths[:1])


def test_diff_list_added_packages(package_paths, index):
    """
    diff should recognize added ``packages``
    """

    # fake an extra package
    extra_package = ['extra-package-1.3.0.whl']
    added, dirty, removed = index.diff(extra_package + package_paths)

    assert added == set(extra_package)
    assert dirty == set()
    assert removed == set()


def test_diff_list_dirty_packages(package_paths, package_data, index):
    """
    diff should recognize dirty ``packages``
    """

    # fake a mtime for the 2 first packages in the past
    mtime = {'mtime': time() - 2 * 24 * 60 * 60}
    index.__dict__['metadata'] = dict(zip(
        package_paths,
        [
            (data.update(mtime) or data) if i < 2 else data  # dict merge
            for i, data in enumerate(package_data)
        ]
    ))

    added, dirty, removed = index.diff(package_paths)

    assert added == set()
    assert dirty == set(package_paths[:2])
    assert removed == set()
