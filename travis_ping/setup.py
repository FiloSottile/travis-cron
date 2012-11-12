#!/usr/bin/env python

from distutils.core import setup

setup(name='Travis ping',
      version='1.0',
      description='Trigger Travis CI builds using API',
      author='Filippo Valsorda',
      author_email='filippo.valsorda@gmail.com',
      url='https://github.com/FiloSottile/travis-cron',
      py_modules=['travis_ping'],
     )
