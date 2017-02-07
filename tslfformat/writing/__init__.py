# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import os.path
import os


logger = logging.getLogger(__name__)




class TSLFWriter(object):
    def __init__(self, tslfdir):
        """
        Get ready for appends
        :param tslfdir:
        """


        self.tslfdir = tslfdir

