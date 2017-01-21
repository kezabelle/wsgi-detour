#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys

sys.dont_write_bytecode = True
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

MISSING_DEPENDENCY = False
try:
    from bottle import route, Bottle
except ImportError:
    sys.stdout.write("You'll need to `pip install bottle` to run this demo\n")
    MISSING_DEPENDENCY = True
try:
    import django
except ImportError:
    sys.stdout.write("You'll need to `pip install Django` to run this demo\n")
    MISSING_DEPENDENCY = True

if MISSING_DEPENDENCY:
    sys.exit(1)

import detour

# ------------------------------------------------------------------------------
# Some raw WSGI responses ...
# ------------------------------------------------------------------------------

def one_view(environ, start_response):
    setup_testing_defaults(environ)
    start_response('200 OK', [('content-type', 'text/plain')])
    return ('Hello world!',)


def another_view(environ, start_response):
    setup_testing_defaults(environ)
    start_response('200 OK', [('content-type', 'text/plain')])
    return ('Another view',)

# ------------------------------------------------------------------------------
# Now we set up a Bottle instance
# ------------------------------------------------------------------------------
bottle_app = Bottle()
@bottle_app.route('/hello')
def bottle_hello_world():
    return u"this went to Bottle"

@bottle_app.route('/goodbye/<var>')
def bottle_goodbye_cruel_world(var):
    return u"%s also went to Bottle" % var

# ------------------------------------------------------------------------------
# Now we set up a Django instance
# ------------------------------------------------------------------------------
from django.conf import settings
settings.configure(
    ROOT_URLCONF=__name__,
    DEBUG=True,
    ALLOWED_HOSTS=['*'],
)
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.conf.urls import url

def django_hello_world(request):
    return HttpResponse(u"I'm from Django!")
urlpatterns = (
    url('^$', django_hello_world),
)
django_app = get_wsgi_application()

# ------------------------------------------------------------------------------
# The WSGI App which Detour wraps over as a fallthrough...
# ------------------------------------------------------------------------------

def fallback(environ, start_response):
    setup_testing_defaults(environ)
    start_response('404 Not Found', [('content-type', 'text/plain')])
    return ('Fallback!',)

# ------------------------------------------------------------------------------
# Example Detour setup.
# ------------------------------------------------------------------------------
application = detour.Detour(app=fallback, mounts=(
    ('/raw/one_view', one_view),
    ('/raw/another_view', another_view),
    ('/bottled', bottle_app),
    ('/django', django_app),
))

if __name__ == '__main__':
    httpd = make_server('', 8080, application)
    print("Running on port 8080")
    httpd.serve_forever()
