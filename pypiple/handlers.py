#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pypiple Request Handlers
------------------------
"""
from webob import Response
from webob.dec import wsgify


class AbstractHandler(object):
    """docstring for """

    def __init__(self, index, mount_points, paths):
        """TODO"""
        self.index = index
        self.mount_points = mount_points
        self.paths = paths
        self._cache = {}

    def cache(self, key, default, *args, **kwargs):
        """TODO"""
        return (
            self.cache.get(key) or  # pylint: disable=no-member
            self.cache.setdefault(key, default(  # pylint: disable=no-member
                *args, **kwargs))
        )

    def expire(self, key):
        """TODO"""
        self._cache[key] = None

    @wsgify
    def __call__(self, req):
        """TODO"""
        changed = self.index.update()

        if changed is not None:
            self.expire(':response')

        # since the character ':' is forbidden for file paths and
        # package names, it will not interfere with 'per-packages' cache
        return Response(self.cache(':response', self.render))

    def render(self):
        """TODO"""
        raise NotImplementedError


# pylint: disable=abstract-method,missing-docstring
class FancyCollectionHandler(AbstractHandler):
    pass


class FancyItemHandler(AbstractHandler):
    pass


class SimpleCollectionHander(AbstractHandler):
    pass


class SimpleItemHandler(AbstractHandler):
    pass
