# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import io
import struct

from tslfformat.framing import HEADER, SEGMENT_TYPE_TO_CLASS

logger = logging.getLogger(__name__)


class SingleFileReader(object):
    """
    Reads in a single TSLF file

    Public instance properties:

        extra_data - binary, extra data readed from TSLF file
    """

    def __init__(self, path):
        """
        :param path: path to TSLF file
        """

        self.file = io.open(path, 'rb')

        if self.file.read(len(HEADER)) != HEADER:
            self.file.close()
            raise IOError(u'Not a valid TSLF file')

        extra_data_len = struct.unpack('!L', self.file.read(4))
        self.extra_data = self.file.read(extra_data_len)

        self.position_after_header = self.file.tell()

    def __iter__(self):
        """
        Sequentially return segments (instances of Segment)

        Close the file afterwards.
        """

        while True:
            seg_type, = struct.unpack('!B', self.file.read(1))
            seg_cls = SEGMENT_TYPE_TO_CLASS[seg_type]
            yield seg_cls.read_from(self.file)

        self.file.close()