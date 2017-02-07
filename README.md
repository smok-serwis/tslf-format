tslf-format
===========

A TSLF framer/writer/manager

TSLF, or Time Series Logging Format, is:
1. A journal for collecting time series data from many sensors. You get a value, you
   pass it to TSLF. TSLF writes it to disk in a durable and fast way.
2. A database - you can actually store these values there!

TSLF is used as storage for (Longshot)[https://github.com/smok-serwis/longshot-python],
however it is generic enough to use as a journal/storage format.

This is compatible with:
* Python 2.7
* Python 3.x
* PyPy
