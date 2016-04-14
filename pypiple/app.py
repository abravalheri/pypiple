#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TODO: doc
"""
from gevent import monkey  # isort:skip
monkey.patch_all()  # isort:skip

import re
from os import getcwd, path
from pkg_resources import resource_filename

import livereload
from selector import Selector
from webob.static import DirectoryApp

from pypiple.handlers import FancyCollectionHandler
from pypiple.index import Index
from pypiple.middleware import filter_path

PREFFIX = '/'
"""Default mount point for pypiple app"""

ASSETS_PATH = resource_filename(__package__, 'assets')
"""Default path for static files"""

PACKAGES_PATH = path.join(getcwd(), 'packages')
"""Default path for packages"""

TEMPLATES_PATH = resource_filename(__package__, 'templates')
"""Default path for templates"""

ASSETS_EXT = 'css|js|ico|png|jpg|svg|gif'
"""Allowed extensions for static files"""

PACKAGES_EXT = 'tar.gz|whl|egg'
"""Allowed extensions for packages"""


def application():
    """TODO"""

    mount_points = {
        'index': PREFFIX,
        'assets': '/'.join([PREFFIX, 'assets']),
        'packages':  '/'.join([PREFFIX, 'packages']),
    }

    paths = {
        'asssets': ASSETS_PATH,
        'packages': PACKAGES_PATH,
        'templates': TEMPLATES_PATH
    }

    index = Index(paths['templates'])

    filters = {
        # filter packages by extension
        'packages': re.compile(
            r'\.({})$'.format(PACKAGES_EXT.replace('.', r'\.')), re.I),
        # filter static files by extension
        'assets': re.compile(
            r'\.({})$'.format(ASSETS_EXT.replace('.', r'\.')), re.I),
    }

    handlers = {
        'index': FancyCollectionHandler(index, mount_points, paths),
        'packages': filter_path(  # pylint: disable=no-value-for-parameter
            DirectoryApp(paths['packages'], index_page=None),
            filters['packages']),
        'assets': filter_path(  # pylint: disable=no-value-for-parameter
            DirectoryApp(paths['assets'], index_page=None),
            filters['assets']),
    }

    routes = [
        (route, {'GET':  handlers[resource]})
        for resource, route in mount_points.items()
    ]

    return Selector(mappings=routes)

app = application()  # pylint: disable=invalid-name

if __name__ == '__main__':
    server = livereload.Server(app)  # pylint: disable=invalid-name

    server.watch(
        'pypiple/static/style.scss', livereload.shell(
            'sassc --sourcemap --source-comments '
            'pypiple/static/style.scss pypiple/static/style.css'))

    server.serve(port=3000, host='0.0.0.0')
