wsgi-detour
===========

:author: Keryn Knight
:version: 0.1.0

Installation instructions
-------------------------

Currently you need to clone it from `GitHub`_ because I have little idea
about how well it works, or if it works at all (though the tests should pass...)

.. |travis_master| image:: https://travis-ci.org/kezabelle/wsgi-detour.svg?branch=master
  :target: https://travis-ci.org/kezabelle/wsgi-detour

==============  ======
Release         Status
==============  ======
master          |travis_master|
==============  ======


What it is
----------

A ``WSGI`` middleware which dispatches requests to different ``WSGI`` applications
based on their path prefix.

Given a standard ``WSGI`` application mounted at ``/``, Detour makes it
possible to re-route requests for, say, ``/my-awesome-app/`` to a different
WSGI app before they ever get to `Django`_ ... which I know is kind of
a niche requirement.

What's so special about it?
---------------------------

Nothing, really. It comes with pre-cythonized C output, for building an
extension module ... so maybe it'll not-slow?

Why I wrote it
--------------

I have `Django`_ application and I have a new part to add which ostensibly could
be a separate microservice, but the easiest way to weld that microservice into
the monolith is to keep the ecosystem pretending it's not separate.

This means wrapping the existing `Django`_ ``WSGI`` ``application`` object
so that auto-reloading works with the new separate app, and avoids needing
to configure the production HTTPd to add additional mount points.

Usage
-----

Whilst it works with any WSGI application (I think), I wrote it to
scratch a specific itch where I wanted an app which ostensibly could
be a microservice, wired up **into** my Django project.

So here's an example of that::

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    from detour import Detour
    application = Detour(application, mounts=(
        ('/my-awesome-microservice', MyFlaskApp),
        ('/some/other/wsgi', MyBottleApp),
    ))

Any alternatives?
-----------------

Yes, plenty. But why use something when I could re-invent the wheel like a
chump? Betting on werkzeug seems like an obvious choice, otherwise.

* `selector`_ - WSGI request delegation. (AKA routing.)
* `wsgirewrite`_ - an implementation of a mod_rewrite compatible URL rewriter
* `urlrelay`_ - passes HTTP requests to a WSGI application based on a matching regular expression..
* `werkzeug.DispatcherMiddleware`_ - combine multiple WSGI applications

Running the tests
-----------------

Quick and dirty, with coverage::

    DETOUR_SKIP_EXTENSIONS=1 python setup.py test

Remove or set ``DETOUR_SKIP_EXTENSIONS`` to ``0`` to have the
Python compiled via `Cython`_ before running the tests.
As this generates no coverage, and includes a completely different
execution, its worth checking both.

There's also a ``tox`` configuration, and I'm largely relying on `Travis`_ for
checking all the build matrix.

The license
-----------

It's the `FreeBSD`_. There's should be a ``LICENSE`` file in the root of the repository, and in any archives.

.. _FreeBSD: http://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29
.. _GitHub: https://github.com/kezabelle/wsgi-detour
.. _Cython: http://cython.readthedocs.io/
.. _Django: http://djangoproject.com/
.. _selector: https://github.com/lukearno/selector
.. _wsgirewrite: https://bitbucket.org/robertodealmeida/wsgirewrite
.. _urlrelay: https://bitbucket.org/lcrees/urlrelay/src
.. _werkzeug.DispatcherMiddleware: http://werkzeug.pocoo.org/docs/0.11/middlewares/#werkzeug.wsgi.DispatcherMiddleware
.. _Travis: https://travis-ci.org/
