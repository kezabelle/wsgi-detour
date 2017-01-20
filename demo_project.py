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

if MISSING_DEPENDENCY:
    sys.exit(1)

import detour



def one_view(environ, start_response):
    setup_testing_defaults(environ)
    start_response('200 OK', [('content-type', 'text/plain')])
    return ('Hello world!',)


def another_view(environ, start_response):
    setup_testing_defaults(environ)
    start_response('200 OK', [('content-type', 'text/plain')])
    return ('Another view',)

bottle_app = Bottle()

@bottle_app.route('/hello')
def index():
    return "this went to Bottle"

@bottle_app.route('/goodbye/<var>')
def index(var):
    return "%r also went to Bottle" % var


def fallback(environ, start_response):
    setup_testing_defaults(environ)
    start_response('404 Not Found', [('content-type', 'text/plain')])
    return ('Fallback!',)

application = detour.Detour(app=fallback, mounts=(
    ('/one_view', one_view),
    ('/another_view', another_view),
    ('/bottled', bottle_app),
))

if __name__ == '__main__':
    httpd = make_server('', 8080, application)
    print("Running on port 8080")
    httpd.serve_forever()
