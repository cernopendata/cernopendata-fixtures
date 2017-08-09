# -*- coding: utf-8 -*-

"""Fixtures for CERN Open Data Portal."""

import os

from setuptools import find_packages, setup

# Get the version string. Cannot be done with import!
version = {}
with open(os.path.join('cernopendata_fixtures',
                       'version.py'), 'rt') as fp:
    exec (fp.read(), version)

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'mock>=1.3.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.4.2',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.6.2',
]

install_requires = [
    'invenio-assets>=1.0.0b6',
    'invenio-base>=1.0.0a9',
    'invenio-celery>=1.0.0b1',
    'invenio-collections>=1.0.0a1',
    'invenio-config>=1.0.0b1',
    'invenio-db[versioning,postgresql]>=1.0.0b3',
    'invenio-indexer>=1.0.0a1',
    'invenio-jsonschemas>=1.0.0a2',
    'invenio-marc21>=1.0.0a1',
    'invenio-oaiserver>=1.0.0a9',
    'invenio-pidstore>=1.0.0b1',
    'invenio-records-rest>=1.0.0a9',
    'invenio-records-ui>=1.0.0a8',
    'invenio-records>=1.0.0b1',
    'invenio-search-ui>=1.0.0a2',
    'invenio-search>=1.0.0a9',
    'invenio-theme>=1.0.0a16',
]

setup(
    name='cernopendata-fixtures',
    version=version['__version__'],
    description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'flask.commands': [
            'fixtures = '
            'cernopendata_fixtures.cli:fixtures',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
)
