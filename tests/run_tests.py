#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import nose


def start(argv=None):
    sys.exitfunc = lambda: sys.stderr.write('Shutting down...\n')

    if argv is None:
        argv = [
            'nosetests',
            '--verbose',
            '--with-coverage',
            '--cover-html', '--cover-html-dir=.htmlcov',
            '--cover-erase',
            '--cover-branches',
            '--cover-package=permtrail',
        ]

    nose.run_exit(argv=argv, defaultTest=os.path.abspath(os.path.dirname(__file__)))

if __name__ == '__main__':
    start(sys.argv)
