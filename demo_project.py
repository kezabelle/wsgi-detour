#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse
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

try:
    from meinheld import server as meinheld_serve
    HAS_MEINHELD = True
except ImportError as e:
    HAS_MEINHELD = False

try:
    from waitress import serve as waitress_serve
    HAS_WAITRESS = True
except ImportError as e:
    HAS_WAITRESS = False

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

def wsgi_via_meinheld(host, port, application):
    meinheld_serve.listen((host, port))
    print("Running using meinheld on port %d" % port)
    meinheld_serve.run(application)

def wsgi_via_waitress(host, port, application):
    print("Running using waitress on port %d" % port)
    waitress_serve(application, host=host, port=port)

def wsgi_via_wsgiref(host, port, application):
    httpd = make_server('', 8080, application)
    print("Running using wsgiref port %d" % port)
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Demo project for wsgi-detour')
    parser.add_argument('-w', '--wsgi', action='store', choices=('wsgiref', 'meinheld', 'waitress'), default='wsgiref')
    args = parser.parse_args(sys.argv[1:])
    if args.wsgi == 'meinheld':
        if HAS_MEINHELD:
            wsgi_via_meinheld('', 8080, application)
        else:
            sys.stdout.write("Could not import requested WSGI publisher: meinheld\n")
    elif args.wsgi == 'waitress':
        if HAS_WAITRESS:
            wsgi_via_waitress('', 8080, application)
        else:
            sys.stdout.write("Could not import requested WSGI publisher: waitress\n")
    else:
        wsgi_via_wsgiref('', 8080, application)
