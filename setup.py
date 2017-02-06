#!/usr/bin/env python
# coding=UTF-8
from setuptools import setup


setup(name=u'tslf-format',
      version='0.1',
      description=u'Journal/database for values. Part of SMOK Z.',
      author=u'DMS Serwis s.c.',
      author_email=u'piotrm@smok.co',
      url=u'http://git.dms-serwis.com.pl/smok-z/tslf-format',
      packages=[
          'tslfformat'
      ],
      requires=['six'],
      tests_require=["nose"],
      test_suite='nose.collector'
     )


