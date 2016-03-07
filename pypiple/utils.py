# -*- coding: utf-8 -*-
__author__ = 'Anderson Bravalheri'
__copyright__ = 'Anderson Bravalheri'
__license__ = 'Mozilla Public License Version 2.0'


def concatenate(*arrays):
    return reduce(lambda x, y: x + y, arrays, [])
