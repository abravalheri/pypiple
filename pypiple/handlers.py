#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pypiple Request Handlers
------------------------
"""
from webob.dec import wsgify

class AbstractHandler(object):
    """docstring for """
    def __init__(self, index, mount_points, paths):
        self.index = index
        self.mount_points = mount_points
        self.paths = paths
        self._cache = {}

    def cache(key, default, *args, **kwargs):
        return (
            self.cache.get(key) or
            self.cache.setdefault(key, default(*args, **kwargs))
        )

    def expire(key):
        self._cache[key] = None

    @wsgify
    def __call__(self, req):
        changed = self.index.update()

        if changed is not None:
            self.expire(':response')

        # since the character ':' is forbidden for file paths and
        # package names, it will not interfere with 'per-packages' cache
        return Response(self.cache(':response', self.render))

    def render(self):
        raise NotImplementedError


class FancyCollectionHandler(AbstractHandler):
    pass


class FancyItemHandler(AbstractHandler):
    pass


class SimpleCollectionHander(AbstractHandler):
    pass


class SimpleItemHandler(AbstractHandler):
    pass
