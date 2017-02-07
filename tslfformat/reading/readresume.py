# coding=UTF-8
"""
Utilities for when you resume writing into a TSLF file
"""
from __future__ import print_function, absolute_import, division
import six
import logging
import collections

from tslfformat.reading.single_file import SingleFileReader
from tslfformat.framing import Bits32ShortCodeDefinition, Bits16ShortCodeDefinition, \
    Bits8ShortCodeDefinition, BaseShortCodeDefinition, SetTimeZero

logger = logging.getLogger(__name__)

TSLFFileParameters = collections.namedtuple('TSLFFileParameters', ('map8', 'map16', 'map32', 't_zero'))


def get_short_codes_from_tslf(path):
    """
    Open a TSLF file, extract all short codes for paths, close the file.
    :param path: path to TSLF file
    :return: TSLFFileParameters instance
    """

    map8, map16, map32 = {}, {}, {}
    t_zero = 0

    for segment in SingleFileReader(path):

        if isinstance(segment, Bits8ShortCodeDefinition):
            map8[segment.path_name] = segment.short_code
        elif isinstance(segment, Bits16ShortCodeDefinition):
            map16[segment.path_name] = segment.short_code
        elif isinstance(segment, Bits32ShortCodeDefinition):
            map32[segment.path_name] = segment.short_code
        elif isinstance(segment, SetTimeZero):
            t_zero = segment.t_zero

    return TSLFFileParameters(map8, map16, map32, t_zero)

