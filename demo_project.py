#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse
import sys

sys.dont_write_bytecode = True
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3

MISSING_DEPENDENCIES = []
try:
    from bottle import route, Bottle
except ImportError:
    MISSING_DEPENDENCIES.append("bottle")
try:
    import django
except ImportError:
    MISSING_DEPENDENCIES.append("Django")

if MISSING_DEPENDENCIES:
    deps = " ".join(MISSING_DEPENDENCIES)
    sys.stdout.write("You'll need to `pip install {}` to run this demo\n".format(deps))
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

def raw_wsgi(environ, start_response):
    setup_testing_defaults(environ)
    start_response('200 OK', [('content-type', 'text/html')])
    data = 'Another view from wsgi-detour==%s, running under Python%s' % (
        detour.get_version(), sys.version_info.major)
    return (bytes(data.encode('utf-8')),)

# ------------------------------------------------------------------------------
# Now we set up a Bottle instance
# ------------------------------------------------------------------------------
bottle_app = Bottle()
@bottle_app.route('/')
def bottle_hello_world():
    return u"this went to Bottle"

@bottle_app.route('/more/<var>')
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

def django_goodbye_cruel_world(request, arg):
    return HttpResponse(u"%s also went to Django" % arg)


urlpatterns = (
    url('^$', django_hello_world),
    url('^more/(?P<arg>.+?)$', django_goodbye_cruel_world),
)
django_app = get_wsgi_application()

# ------------------------------------------------------------------------------
# The WSGI App which Detour wraps over as a fallthrough...
# ------------------------------------------------------------------------------

def fallback(environ, start_response):
    setup_testing_defaults(environ)
    start_response('404 Not Found', [('content-type', 'text/html')])
    data = """
    Fallback from wsgi-detour==%s, running under Python%s
    <ul>
    <li><a href="/raw/">a raw WSGI app</a></li>
    <li><a href="/bottled/">a Bottle app</a>
        <ul>
            <li><a href="/bottled/more/yes">a Bottle view accepting an argument</a></li>
            <li><a href="/bottled/nope">a Bottle error page</a></li>
        </ul>
    </li>
    <li><a href="/django/">a Django app</a>
        <ul>
            <li><a href="/django/more/yes">a Django view accepting an argument</a></li>
            <li><a href="/django/nope">a Django error page</a></li>
        </ul>
    </li>
    </ul>
    """ % (detour.get_version(), sys.version_info.major)
    return (bytes(data.encode('utf-8')),)

# ------------------------------------------------------------------------------
# Example Detour setup.
# ------------------------------------------------------------------------------
mounts = [
    ('/raw', raw_wsgi),
    ('/bottled', bottle_app),
    ('/django', django_app),
]
application = detour.Detour(app=fallback, mounts=mounts)

def wsgi_via_meinheld(host, port, application):
    meinheld_serve.listen((host, port))
    print("Running using meinheld on port %d" % port)
    meinheld_serve.run(application)

def wsgi_via_waitress(host, port, application):
    print("Running using waitress on port %d" % port)
    waitress_serve(application, host=host, port=port)

def wsgi_via_wsgiref(host, port, application):
    httpd = make_server(host, 8080, application)
    print("Running using wsgiref port %d" % port)
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Demo project for wsgi-detour')
    parser.add_argument('-w', '--wsgi', action='store', choices=('wsgiref', 'meinheld', 'waitress'), default='wsgiref')
    args = parser.parse_args(sys.argv[1:])
    if args.wsgi == 'meinheld':
        if HAS_MEINHELD:
            run_func = wsgi_via_meinheld
        else:
            sys.stdout.write("Could not import requested WSGI publisher: meinheld\n")
            sys.exit(2)
    elif args.wsgi == 'waitress':
        if HAS_WAITRESS:
            run_func = wsgi_via_waitress
        else:
            sys.stdout.write("Could not import requested WSGI publisher: waitress\n")
            sys.exit(2)
    else:
        run_func = wsgi_via_wsgiref

    try:
        version_str = ".".join(str(x) for x in sys.version_info[:3])
        sys.stdout.write("Running demo project via Python %s\n" % (version_str,))
        sys.stdout.write("You can halt this with KeyboardInterrupt (Ctrl-C or whatever)\n")
        run_func('', 8080, application)
    except KeyboardInterrupt:
        sys.stdout.write("\rTerminated by KeyboardInterrupt\n")
