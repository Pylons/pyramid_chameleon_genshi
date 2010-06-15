##############################################################################
#
# Copyright (c) 2008-2010 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__ = '0.2'

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'setuptools',
    'repoze.bfg',
    'Chameleon',
    ]

setup(name='repoze.bfg.chameleon_genshi',
      version=__version__,
      description=('chameleon.genshi template bindings for the repoze.bfg web '
                   'framework'),
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        ],
      keywords='bfg repoze.bfg genshi chameleon templates',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://bfg.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze', 'repoze.bfg'],
      zip_safe=False,
      tests_require = requires,
      install_requires = requires,
      test_suite="repoze.bfg.chameleon_genshi.tests",
      entry_points = """\
      """
      )

