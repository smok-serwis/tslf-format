# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import os
import io
import os.path
from tslfformat.framing import BaseSegment
from tslfformat.reading.readresume import get_short_codes_from_tslf
logger = logging.getLogger(__name__)


class SingleFileWriter(object):
    """
    Writes to a single TSLF file.

    This does not handle flushing, but supports short codes and tzero
    """

    def __init__(self, path):
        """
        Create/open a TSLF file.

        Not thread safe if other SingleFileWriters are being created simultaneously.

        :param path: path to file. If does not exist, will be created.
        """

        self.sc8_map = {}   # path name => 8 bit short code
        self.sc16_map = {}   # path name => 16 bit short code
        self.sc32_map = {}   # path name => 32 bit short code
        self.t_zero = 0     # tzero, in millis

        if not (os.path.exists(path) and os.stat(path).st_size >= 16):
            self.file = open(path, 'wb')
            self.file.write(b'TSLFFORMAT00\x00\x00\x00\x00')
            self.sync()
        else:
            # retrieve all short codes, we might need them
            ps = get_short_codes_from_tslf(path)

            self.sc8_map, self.sc16_map, self.sc32_map, self.t_zero = ps.map8, ps.map16, ps.map32, ps.t_zero

            self.file = open(path, 'ab')

    def write_segments(self, *args):
        """
        Write (many) segment(s) to the file.

        Pass segments as argument. You can also pass binary object,
        file.write() will be called on it.
        """

        # since file is already properly buffered, we can just do this

        for data in args:
            if isinstance(data, BaseSegment):
                data.write_to(self.file)
            else:
                self.file.write(data)

    def sync(self):
        """
        Make sure all data written so far hits disk.
        """
        self.file.flush()
        try:
            os.fsyncdata(self.file.fileno())
        except AttributeError:  # Windows?
            os.fsync(self.file.fileno())

    def close(self):
        """
        Sync. Close this TSLF file.
        """
        self.sync()
        self.file.close()
