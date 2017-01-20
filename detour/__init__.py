# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from collections import OrderedDict
from operator import itemgetter

__version_info__ = '0.1.0'
__version__ = '0.1.0'
version = '0.1.0'
VERSION = '0.1.0'

def get_version():
    return version  # pragma: no cover


class DetourException(NotImplementedError):
    pass


class EntryPoint(tuple):
    'EntryPoint(wsgi_app, short_check, long_check, long_check_length, continue_on_exceptions)'

    __slots__ = ()

    _fields = ('wsgi_app', 'short_check', 'long_check', 'long_check_length', 'continue_on_exceptions')

    def __new__(_cls, wsgi_app, short_check, long_check, long_check_length, continue_on_exceptions):
        'Create new instance of EntryPoint(wsgi_app, short_check, long_check, long_check_length, continue_on_exceptions)'
        return tuple.__new__(_cls, (wsgi_app, short_check, long_check, long_check_length, continue_on_exceptions))

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new EntryPoint object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 5:
            raise TypeError('Expected 5 arguments, got %d' % len(result))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'EntryPoint(wsgi_app=%r, short_check=%r, long_check=%r, long_check_length=%r, continue_on_exceptions=%r)' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        'Return a new EntryPoint object replacing specified fields with new values'
        result = _self._make(map(kwds.pop, ('wsgi_app', 'short_check', 'long_check', 'long_check_length', 'continue_on_exceptions'), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    __dict__ = property(_asdict)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'
        pass

    wsgi_app = property(itemgetter(0), doc='Alias for field number 0')
    short_check = property(itemgetter(1), doc='Alias for field number 1')
    long_check = property(itemgetter(2), doc='Alias for field number 2')
    long_check_length = property(itemgetter(3), doc='Alias for field number 3')
    continue_on_exceptions = property(itemgetter(4), doc='Alias for field number 4')


def prepare_entrypoint(position, prefix, handler, exceptions=(DetourException,)):
    return EntryPoint(wsgi_app=handler, short_check='',
                      long_check=prefix,
                      long_check_length=0,
                      continue_on_exceptions=exceptions)


def prepare_entrypoints(entrypoints):
    for position, entrypoint_config in enumerate(entrypoints, start=1):
        mounter = prepare_entrypoint(position, *entrypoint_config)
        yield mounter


class Detour(object):
    __slots__ = ("app", "entrypoints")

    def __init__(self, app, mounts):
        self.app = app
        self.entrypoints = tuple(prepare_entrypoints(entrypoints=mounts))

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        script_name = environ.get('SCRIPT_NAME', '')
        entrypoints = self.entrypoints
        for mount_entry in entrypoints:
            pass
        # Return the default WSGI publisher this is wrapping over.
        fallback = self.app
        return fallback(environ, start_response)
