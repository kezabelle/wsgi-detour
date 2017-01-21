# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import pytest

from detour import Detour, get_version, VERSION


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
    assert error_message in exc.value


def test_informative_error_if_missing_slash_at_start():
    apps = [
        ('wheee', None),
    ]
    with pytest.raises(ValueError) as exc:
        Detour(None, apps)
    error_message = "Mount Point #1 must start with a '/', got 'wheee' " \
                    "for handler: None"
    assert error_message in exc.value


def test_informative_error_if_trying_to_mount_at_root():
    apps = [
        ('/', None),
    ]
    with pytest.raises(ValueError) as exc:
        Detour(None, apps)
    error_message = "Mount Point #1 tried to mount None at root, which isn't " \
                    "supported. The fallback WSGI application should be " \
                    "handling these requests."
    assert error_message in exc.value


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
