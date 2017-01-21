#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

from setuptools import Extension
from setuptools import setup
from setuptools.command.test import test as TestCommand
if sys.version_info[0] == 2:
    # get the Py3K compatible `encoding=` for opening files.
	from io import open
try:
    from Cython.Build import cythonize
    HAS_CYTHON = True
except ImportError as e:
    HAS_CYTHON = False

HERE = os.path.abspath(os.path.dirname(__file__))


class PyTest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def make_readme(root_path):
    consider_files = ("README.rst", "LICENSE", "CHANGELOG", "CONTRIBUTORS")
    for filename in consider_files:
        filepath = os.path.realpath(os.path.join(root_path, filename))
        if os.path.isfile(filepath):
            with open(filepath, mode="r", encoding="utf-8") as f:
                yield f.read()

LICENSE = "BSD License"
URL = ""
LONG_DESCRIPTION = "\r\n\r\n----\r\n\r\n".join(make_readme(HERE))
SHORT_DESCRIPTION = ""
KEYWORDS = (
    "wsgi",
    "redirect",
    "middlware",
    "wsgi-detour",
)

SKIP_EXTENSIONS = bool(int(os.environ.get('DETOUR_SKIP_EXTENSIONS', 0)))
extensions = ()
if SKIP_EXTENSIONS is False:
    ext = '.py' if HAS_CYTHON else '.c'
    extensions = [Extension("detour.__init__", ["detour/__init__" + ext])]
    if HAS_CYTHON:
        extensions = cythonize(extensions, force=True)
        sys.stdout.write("Cython extension will be built\n")
    else:
        sys.stdout.write("C extension will be built\n")
else:
    sys.stdout.write("Pure python mode requested\n")

setup(
    name="wsgi-detour",
    version="0.1.0",
    author="Keryn Knight",
    author_email="python-wsgi-detour@kerynknight.com",
    maintainer="Keryn Knight",
    maintainer_email="python-wsgi-detour@kerynknight.com",
    description=SHORT_DESCRIPTION[0:200],
    long_description=LONG_DESCRIPTION,
    packages=[
        "detour",
    ],
    ext_modules=extensions,
    include_package_data=True,
    install_requires=[
    ],
    tests_require=[
        "pytest>=2.6",
        "pytest-cov>=1.8",
        "pytest-remove-stale-bytecode>=1.0",
        "pytest-catchlog>=1.2",
    ],
    cmdclass={"test": PyTest},
    zip_safe=False,
    keywords=" ".join(KEYWORDS),
    license=LICENSE,
    url=URL,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: {}".format(LICENSE),
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
    ],
)
