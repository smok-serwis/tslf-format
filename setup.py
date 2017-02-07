#!/usr/bin/env python
# coding=UTF-8
from setuptools import setup


setup(name=u'tslf-format',
      version='0.1',
      description=u'Journal/database for values.',
      author=u'DMS Serwis s.c.',
      author_email=u'piotrm@smok.co',
      url=u'https://github.com/smok-serwis/tslf-format',
      download_url='https://github.com/smok-serwis/tslf-format/archive/v0.1.zip',
      packages=[
          'tslfformat',
          'tslfformat.framing',
          'tslfformat.reading',
          'tslfformat.writing',
      ],
      requires=['six'],
      tests_require=["nose"],
      test_suite='nose.collector'
     )


