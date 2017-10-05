# -*- coding: utf-8 -*-

import re
import os

from pip.req import parse_requirements
from setuptools import setup, find_packages


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
    packages=find_packages('.', exclude=['tests*', 'docs*', 'javascript*']),
    include_package_data=True,
    install_requires=[str(r.req) for r in parse_requirements('./requirements.txt', session=False)],
    extras_require={
        'perms': [
            'djangorestframework'
        ]
    },
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
