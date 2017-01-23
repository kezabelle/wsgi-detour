# -*- coding: utf-8 -*-
#cython: language_level=3, boundscheck=True, wraparound=False, embedsignature=True, always_allow_keywords=True
from __future__ import absolute_import

# As far as I can tell, once an __init__.so exists, this file is basically
# ignored ... because I've tried compiling it locally and then doing
# raise ValueError("__init__.py loaded when __init__.so should have been loaded")
# as suggested by http://stackoverflow.com/a/32067984
# and the error never comes up.

__version_info__ = '0.1.0'
__version__ = '0.1.0'
version = '0.1.0'
VERSION = '0.1.0'

def get_version():
    return version


class EntryPoint(object):
    __slots__ = ('wsgi_app', 'short_check', 'long_check', 'long_check_length')

    def __init__(self, wsgi_app, short_check, long_check, long_check_length):
        self.wsgi_app = wsgi_app
        self.short_check = short_check
        self.long_check = long_check
        self.long_check_length = long_check_length

    def __repr__(self):
        'Return a nicely formatted representation string'
        return u'EntryPoint(wsgi_app=%(wsgi_app)r, ' \
               u'short_check=%(short_check)r, long_check=%(long_check)r, ' \
               u'long_check_length=%(long_check_length)r)' % {
                   'wsgi_app': self.wsgi_app,
                   'short_check': self.short_check,
                   'long_check': self.long_check,
                   'long_check_length': self.long_check_length,
               }

    def __getstate__(self):
        return {
            'wsgi_app': self.wsgi_app,
            'short_check': self.short_check,
            'long_check': self.long_check,
            'long_check_length': self.long_check_length,
        }

    def __setstate__(self, items):
        self.wsgi_app = items.get('wsgi_app')
        self.short_check = items.get('short_check')
        self.long_check = items.get('long_check')
        self.long_check_length = items.get('long_check_length')


def prepare_entrypoint(position, prefix, handler):
    short_check = prefix[:2]
    starts_with = short_check[:1]
    SLASH = "/"
    if starts_with != SLASH:
        msg = u"Mount Point #%(num)s must start with a " \
              u"'%(prefix)s', got '%(mountpoint)s' " \
              u"for handler: %(handler)r" % {
                  'num': position,
                  'prefix': SLASH,
                  'mountpoint': prefix,
                  'handler': handler,
              }
        raise ValueError(msg)
    if short_check == SLASH:
        msg = u"Mount Point #%(num)s tried to mount %(handler)r at root, " \
              u"which isn't supported. The fallback WSGI application " \
              u"should be handling these requests." % {
                  'num': position,
                  'handler': handler,
              }
        raise ValueError(msg)
    long_check_length = len(prefix)
    return EntryPoint(wsgi_app=handler, short_check=short_check,
                      long_check=prefix,
                      long_check_length=long_check_length)


def prepare_entrypoints(entrypoints):
    results = []
    for position, entrypoint_config in enumerate(entrypoints, start=1):
        if hasattr(entrypoint_config, 'keys') and callable(entrypoint_config.keys):
            mounter = prepare_entrypoint(position, **entrypoint_config)
        else:
            entrypoint_config_length = len(entrypoint_config)
            if entrypoint_config_length < 2:
                msg = u"Mount Point #%(num)s must have 2 items, a mountpoint like " \
                      u"'/app', and a WSGI application instance. " \
                      u"Example: ('/app1', MyAppHandler())" % {
                          'num': position,
                      }
                raise ValueError(msg)
            mounter = prepare_entrypoint(position, *entrypoint_config)
        results.append(mounter)
    return results


class Detour(object):
    __slots__ = ("app", "entrypoints")

    def __init__(self, app, mounts):
        self.app = app
        self.entrypoints = prepare_entrypoints(entrypoints=mounts)

    def handle(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '').encode('iso-8859-1')
        script_name = environ.get('SCRIPT_NAME', '').encode('iso-8859-1')
        entrypoints = self.entrypoints
        for mount_entry in entrypoints:
            # Grab first N chars of URL to compare
            short_slice = path_info[:2]
            short_check = mount_entry.short_check

            if short_slice == short_check:
                # first N chars of URL/mount were correct, now do the
                # full comparison for the mountpoint.
                long_slice = path_info[:mount_entry.long_check_length]
                long_check = mount_entry.long_check

                if long_slice == long_check:
                    # Rejig the environ dict's data and dispatch to the given
                    # WSGI publisher.
                    environ['SCRIPT_NAME'] = '%s%s' % (script_name, long_check)
                    environ['PATH_INFO'] = path_info.replace(long_check, '')
                    wsgi_application = mount_entry.wsgi_app
                    return wsgi_application(environ, start_response)
        # Return the default WSGI publisher this is wrapping over.
        fallback = self.app
        return fallback(environ, start_response)

    def __call__(self, environ, start_response):
        return self.handle(environ, start_response)

    def __repr__(self):
        mounts = [(x.long_check, x.wsgi_app) for x in self.entrypoints]
        return 'Detour(app=%(app)r, mounts=%(mounts)r)' % {
            'app': self.app,
            'mounts': mounts,
        }

    def __getstate__(self):
        return {
            'app': self.app,
            'entrypoints': self.entrypoints,
        }

    def __setstate__(self, items):
        self.app = items.get('app')
        self.entrypoints = items.get('entrypoints')
