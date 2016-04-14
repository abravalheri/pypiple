#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pypiple Middleware
------------------

Usefull Middleware for WSGI applications.

- ``filter_path`` can be used to abort requests based on the path, e.g. allow
    access for static files with specifics extensions.
"""

from webob.dec import wsgify
from webob.exc import HTTPNotFound


@wsgify.middleware
def filter_path(req, app, path_filter):
    r"""Restrict access to requested paths

    Arguments:
        path_filter: object with a `search` method that returns Truthy or Falsy
            values when analyzing the given path (usually a regex object)::

                filter_path(app, re.compile(r'\.html$'))

    Raises:
        HTTPNotFound if the ``path_filter.search(request.path)`` returns a
        falsy value

    Returns:
        The original app
    """
    if not path_filter.search(req.path):
        raise HTTPNotFound

    return app
