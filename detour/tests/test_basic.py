# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import os
import pickle
import sys

import pytest

from detour import Detour, get_version, VERSION

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3
if PY3:
    unicode = str


def test_get_version():
    assert get_version() == VERSION


def test_informative_error_if_not_enough_args():
    apps = [
        ('wheee',),
    ]
    with pytest.raises(ValueError) as exc:
        Detour(None, apps)
    error_message = "Mount Point #1 must have 2 items, a mountpoint like " \
                    "'/app', and a WSGI application instance. " \
                    "Example: ('/app1', MyAppHandler())"
    assert error_message in unicode(exc.value)


def test_informative_error_if_missing_slash_at_start():
    apps = [
        ('wheee', None),
    ]
    with pytest.raises(ValueError) as exc:
        Detour(None, apps)
    error_message = "Mount Point #1 must start with a '/', got 'wheee' " \
                    "for handler: None"
    assert error_message in unicode(exc.value)


def test_informative_error_if_trying_to_mount_at_root():
    apps = [
        ('/', None),
    ]
    with pytest.raises(ValueError) as exc:
        Detour(None, apps)
    error_message = "Mount Point #1 tried to mount None at root, which isn't " \
                    "supported. The fallback WSGI application should be " \
                    "handling these requests."
    assert error_message in unicode(exc.value)


@pytest.mark.parametrize("entry_point_config", [
    ('/wheee', None),
    {'prefix': '/wheee', 'handler': None}
])
def test_building_entrypoints_ok(entry_point_config):
    apps = [
        entry_point_config,
    ]
    app = Detour(None, apps)
    assert app.app is None
    assert len(app.entrypoints) == 1
    ep = app.entrypoints[0]
    assert ep.short_check == '/w'
    assert ep.long_check == '/wheee'
    assert ep.long_check_length == len('/wheee')
    assert ep.long_check_length == 6
    ep_repr = "EntryPoint(wsgi_app=None, short_check='/w', long_check='/wheee', long_check_length=6)"
    assert repr(ep) == ep_repr


def _fallback(environ, start_response):
    start_response('200 OK', [('content-type', 'text/html')])
    return ('fallback',)


def test_fallback_empty_mounts():
    def start_response(*args, **kwargs):
        return args, kwargs


    app = Detour(_fallback, ())
    environ = {}
    response = app(environ, start_response)
    assert response == ('fallback',)


def test_fallback_because_misses_short_check():
    def start_response(*args, **kwargs):
        return args, kwargs

    def test_app(environ, start_response):
        start_response('200 OK', [('content-type', 'text/html')])
        return ('test app',)

    app = Detour(_fallback, (
        ('/xoxo', test_app),
    ))
    environ = {
        'PATH_INFO': "/test/request/"
    }
    response = app(environ, start_response)
    assert response == ('fallback',)


def test_fallback_because_misses_long_check():
    def start_response(*args, **kwargs):
        return args, kwargs

    def test_app(environ, start_response):
        start_response('200 OK', [('content-type', 'text/html')])
        return ('test app',)

    app = Detour(_fallback, (
        ('/tesnope', test_app),
    ))
    environ = {
        'PATH_INFO': "/test/request/"
    }
    response = app(environ, start_response)
    assert response == ('fallback',)


def test_dispatched_to_app():
    def start_response(*args, **kwargs):
        return args, kwargs

    def test_app(environ, start_response):
        start_response('200 OK', [('content-type', 'text/html')])
        return ('test app',)

    app = Detour(_fallback, (
        ('/test', test_app),
    ))
    environ = {
        'PATH_INFO': "/test/request/",
        'SCRIPT_NAME': 'HELLO',
    }
    response = app(environ, start_response)
    assert response == ('test app',)
    assert environ == {'PATH_INFO': '/request/',
                       'SCRIPT_NAME': 'HELLO/test'}


def test_repr():
    def test_app(environ, start_response):
        start_response('200 OK', [('content-type', 'text/html')])
        return ('test app',)
    app = Detour(_fallback, (
        ('/test', test_app),
        ('/another', test_app),
        ('/whee', test_app),
    ))
    _repr_ = repr(app)
    assert _repr_.startswith("Detour(app=")
    assert ", mounts=[" in _repr_
    assert _repr_.endswith("])")


def picklable_app(environ, start_response):
    start_response('200 OK', [('content-type', 'text/plain')])
    return ('pickle pockle',)


@pytest.mark.skipif(bool(int(os.getenv('DETOUR_SKIP_EXTENSIONS', 0))) is False,
                    reason="I dunno how to make cython stuff picklable yet tbh")
def test_pickle():
    app = Detour(_fallback, (
        ('/test', picklable_app),
    ))
    pickled = pickle.dumps(app)
    unpickled = pickle.loads(pickled)
