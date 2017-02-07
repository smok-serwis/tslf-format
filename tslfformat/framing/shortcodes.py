# coding=UTF-8
"""
Short codes - types, a database/allocator object, and so on
"""
from __future__ import print_function, absolute_import, division
import six
import logging

logger = logging.getLogger(__name__)


class ShortCodeType(object):
    BITS_8 = 0      # 8 bit short code
    BITS_16 = 1     # 16 bit short code
    BITS_32 = 2     # 32 bit short code



class ShortCodeDatabase(object):
    def __init__(self):
        self.path_to_sc = {}    # dict(path => sc_type, sc)
        self.sc_to_path = {}    # dict (sc_type, sc => path)

    def notify(self, path_name, sc_type, sc):
        """
        Inform the database that path name has a particular short code.

        Used by reader when reading in a database from a TSLF file.
        """

    def allocate(self, path_name):
        """
        Return a new short code for a path.

        This does not imply that it's in effect - call notify for that
        :param path_name:
        :return: sc_Type, sc
        """

