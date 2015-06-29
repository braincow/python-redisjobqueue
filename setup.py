#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name='redisjobqueue',
	version='0.1.0',
	packages=find_packages(),
	description='Non-blocking job queue for Redis backend with distributed locking mechanism to prevent double work.',
	author='Antti Peltonen',
	author_email='antti.peltonen@iki.fi',
	url='https://github.com/braincow/python-redisjobqueue',
	install_requires=['redis', 'redlock-py']
	)
