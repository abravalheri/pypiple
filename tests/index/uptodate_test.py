#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automated tests for pypiple.index.Index#uptodate
"""
import os
import time

from pypiple.index import Index

__author__ = 'Anderson Bravalheri'
__copyright__ = 'Anderson Bravalheri'
__license__ = 'Mozilla Public License Version 2.0'


def test_uptodate_returns_true_when_dir_is_not_modified(tmpdir):
    """
    uptodate should return true when directory is not modified
    since index last update
    """
    index = Index(str(tmpdir))  # empty directory
    index.update()  # => update will modify index mtime to `now`

    time.sleep(0.01)
    assert index.uptodate()


def test_uptodate_returns_false_when_dir_is_modified(tmpdir):
    """
    uptodate should return false when directory is modified
    after index last update
    """
    tmp = str(tmpdir)
    index = Index(tmp)  # empty directory
    index.update()  # => update will modify index mtime to `now`

    # touch directory to change real mtime
    time.sleep(0.01)
    with open(os.path.join(tmp, 'test.txt'), 'w'):
        pass

    assert not index.uptodate()
