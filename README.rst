wsgi-detour
===========

:author: Keryn Knight
:version: 0.1.0

Installation instructions
-------------------------

Currently you need to clone it from `GitHub`_ because I have little idea
about how well it works.


What it is
----------

A ``WSGI`` middleware which dispatches requests to different ``WSGI`` applications
based on their path prefix.

Given a standard `Django`_ application mounted at ``/``, Detour makes it
possible to re-route requests for, say, ``/my-awesome-app/`` to a different
WSGI app before they ever get to `Django`_ ... which I know is kind of
a niche requirement.

What's so special about it?
---------------------------

Nothing, really.


Why I wrote it
--------------

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


Running the tests
-----------------

Quick and dirty, with coverage::

    DETOUR_SKIP_EXTENSIONS=1 python setup.py test

Remove or set ``DETOUR_SKIP_EXTENSIONS`` to ``0`` to have the
Python compiled via `Cython`_ before running the tests.
As this generates no coverage, and includes a completely different
execution, its worth checking both.

The license
-----------

It's the `FreeBSD`_. There's should be a ``LICENSE`` file in the root of the repository, and in any archives.

.. _FreeBSD: http://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29
.. _GitHub: https://github.com/kezabelle/wsgi-detour
.. _Cython: http://cython.readthedocs.io/
.. _Django: http://djangoproject.com/
