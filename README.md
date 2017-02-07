tslf-format
===========

[![Build Status](https://travis-ci.org/smok-serwis/tslf-format.svg)](https://travis-ci.org/smok-serwis/tslf-format)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)]()

A TSLF framer/writer/manager

TSLF, or Time Series Logging Format, is:

1. A journal for collecting time series data from many sensors. You get a value, you
   pass it to TSLF. TSLF writes it to disk in a durable and fast way.
2. A database - you can actually store these values there!

TSLF is used as temporary transactional storage for 
[Longshot]([https://github.com/smok-serwis/longshot-python)
however it is generic enough to use as a journal/storage format.
Longshot removes data synchronized with server - TSLF allows for that, because 
it's a journal too.

This is compatible with:
* Python 2.7
* Python 3.x
* PyPy

# What's this
A TSLF file is a two dimensional map of (tag::utf8, timestamp::qword) => value::binary,
sorted by timestamp.

Tags are means to be reused many times, and therefore are compressed with a form of RLE.
