# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import os
import io
import os.path
from tslfformat.framing import BaseSegment

logger = logging.getLogger(__name__)


class SingleFileWriter(object):
    """
    Writes to a single TSLF file.

    This does not handle flushing.
    """

    def __init__(self, path):
        """
        Create/open a TSLF file.

        Not thread safe if other SingleFileWriters are being created simultaneously.

        :param path: path to file. If does not exist, will be created.
        """

        if os.path.exists(path) and os.stat(path).st_size >= 16:
            # check for both existence, and that header was successfully written out
            self.file = io.open(path, 'ab')
        else:
            self.file = open(path, 'wb')
            self.file.write(b'TSLFFORMAT00\x00\x00\x00\x00')
            self.sync()

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
