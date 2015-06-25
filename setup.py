#!/usr/bin/env python

from distutils.core import setup

setup(name='redisjobqueue',
	version='0.0.1',
	description='Non-blocking job queue for Redis backend with distributed locking mechanism to prevent double work.',
	author='Antti Peltonen',
	author_email='antti.peltonen@iki.fi',
	url='https://github.com/braincow/python-redisjobqueue',
	packages=['redisjobqueue']
	)