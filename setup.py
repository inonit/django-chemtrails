# -*- coding: utf-8 -*-

import re
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

setup(
    name='django-chemtrails',
    version=get_version('chemtrails'),
    description='Graphing Django in Neo4j',
    long_description='Graphing Django in Neo4j slightly longer.',
    author='Rolf Håvard Blindheim',
    author_email='rhblind@gmail.com',
    url='https://github.com/inonit/django-chemtrails',
    download_url='https://github.com/inonit/django-chemtrails.git',
    license='MIT License',
    packages=[
        'chemtrails'
    ],
    include_package_data=True,
    install_requires=[
        'Django>=1.10,<2.0',
        'libcypher-parser-python>=0.0.4',
        'neomodel==3.1.0',
        'requests[security]'
    ],
    tests_require=[
        'nose',
        'coverage',
        'django-autofixture',
        'djangorestframework',
        'psycopg2>=2.6.2'
    ],
    zip_safe=False,
    test_suite='tests.run_tests.start',
    classifiers=[
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
