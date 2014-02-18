#!/usr/bin/env python
import os
import sys

from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASE_ENGINE='sqlite3',
        SITE_ID=1,
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'piston',
            'piston.test_integration.testapp',
            ],
        TEMPLATE_DIRS=[
            os.path.join(os.path.dirname(__file__), 'templates'),
            ],
        ROOT_URLCONF='piston.test_integration.urls',
        MIDDLEWARE_CLASSES=[
            'piston.middleware.ConditionalMiddlewareCompatProxy',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'piston.middleware.CommonMiddlewareCompatProxy',
            'django.contrib.auth.middleware.AuthenticationMiddleware'
            ]
        )

from django.test.simple import run_tests


def runtests(*test_args):
    if not test_args:
        test_args = ['testapp', 'piston']
    parent = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
    )
    sys.path.insert(0, parent)
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
