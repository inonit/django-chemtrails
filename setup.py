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
    name='django-permtrail',
    version=get_version('permtrail'),
    description='Neo4j Permission Backend for Django',
    long_description='Calculate permissions based on entity relationship in a Neo4j graph',
    author='Rolf Håvard Blindheim',
    author_email='rhblind@gmail.com',
    url='https://github.com/inonit/django-permtrail',
    download_url='https://github.com/inonit/django-permtrail.git',
    license='MIT License',
    packages=[
        'permtrail',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=1.8.0',
    ],
    tests_require=[
        'nose',
        'coverage',
        'django-autofixture',
    ],
    zip_safe=False,
    test_suite='tests.run_tests.start',
    classifiers=[
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
