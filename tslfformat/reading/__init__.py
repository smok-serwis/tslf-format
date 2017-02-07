# coding=UTF-8
"""
Reading and parsing TSLF file
"""
from __future__ import print_function, absolute_import, division
import six
import logging

logger = logging.getLogger(__name__)


from tslfformat.reading.single_file import SingleFileReader
from tslfformat.reading.readresume import get_short_codes_from_tslf
