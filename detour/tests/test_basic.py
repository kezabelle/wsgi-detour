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
