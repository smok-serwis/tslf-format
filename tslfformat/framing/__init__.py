# coding=UTF-8
"""
Reading and writing TSLF records.
"""
from __future__ import print_function, absolute_import, division
import six
import logging
import struct


logger = logging.getLogger(__name__)


HEADER = b'TSLFFORMAT00'


class ShortCodeType(object):
    BITS_8 = 0      # 8 bit short code
    BITS_16 = 1     # 16 bit short code
    BITS_32 = 2     # 32 bit short code


class PathpointValueStatus(object):
    OK = 0b00
    MALFORMED = 0b01
    TIMEOUT = 0b10
    INVALID = 0b11



class BaseSegment(object):
    """Abstract base segment"""

    def write_to(self, f):
        """
        Write this binary representation into file f.

        Includes segment header

        :param f: file object
        :return: bytes written
        """
        raise Exception('Abstract')

    @classmethod
    def read_from(f):
        """
        Return this instance of a segment. Segment type byte has already
        been read - that's how this class was found!

        :param f: file to read from
        :return: an instance of self
        """
        raise Exception('Abstract')


class BaseShortCodeDefinition(BaseSegment):
    """
    Base class for short code definitions (0x00 - 0x02)
    """

    BITNESS_CODE = None     # this is used in child classes
    SEGMENT_CODE = None

    def __init__(self, path_name, short_code):
        """
        :param path_name: text or bytes, name of the path
        :param short_code: int, short code
        """
        self.path_name = path_name.decode('utf8') if isinstance(path_name, six.binary_type) else path_name
        self.short_code = short_code

    def write_to(self, f):
        """
        Write out the path name path
        """
        p = self.path_name.encode('utf8')
        f.write(struct.pack('!BH', self.SEGMENT_CODE, len(p)))
        f.write(p)
        f.write(struct.pack(self.BITNESS_CODE, self.short_code))

    @classmethod
    def read_from(cls, f):
        """Read in path name (2 byte len + data), return a unicode"""
        ln, = struct.unpack('!H', f.read(2))
        path_name = f.read(ln).decode('utf8')
        short_code, = struct.unpack(cls.BITNESS_CODE, f.read(struct.calcsize(cls.BITNESS_CODE)))
        return cls(path_name, short_code)

class Bits8ShortCodeDefinition(BaseShortCodeDefinition):
    BITNESS_CODE = '!B'
    SEGMENT_CODE = ShortCodeType.BITS_8

class Bits16ShortCodeDefinition(BaseShortCodeDefinition):
    BITNESS_CODE = '!H'
    SEGMENT_CODE = ShortCodeType.BITS_16

class Bits32ShortCodeDefinition(BaseShortCodeDefinition):
    BITNESS_CODE = '!L'
    SEGMENT_CODE = ShortCodeType.BITS_32


class SetTimeZero(BaseSegment):
    def __init__(self, t_zero):
        """:param t_zero: time zero in milliseconds, UNIX epoch"""
        self.t_zero = int(t_zero)

    def write_to(self, f):
        f.write(struct.pack('!BQ', 0x03, self.t_zero))

    @classmethod
    def read_from(f):
        t_zero, = struct.unpack('!Q', f.read(8))
        return SetTimeZero(t_zero)


class ConsiderSyncedUntil(BaseSegment):
    def __init__(self, until):
        """:param until: time zero in milliseconds, UNIX epoch"""
        self.until = int(until)

    def write_to(self, f):
        f.write(struct.pack('!BQ', 0x08, self.until))

    @classmethod
    def read_from(f):
        until, = struct.unpack('!Q', f.read(8))
        return ConsiderSyncedUntil(until)



class BaseValue(BaseSegment):
    """0x04-0x07"""

    SHORT_CODE_BITNESS = None
    SEGMENT_CODE = None

    def __init__(self, path_name, timestamp, value_status, value):
        pass



SEGMENT_TYPE_TO_CLASS = {
    0x00: Bits8ShortCodeDefinition,
    0x01: Bits16ShortCodeDefinition,
    0x02: Bits32ShortCodeDefinition,
    0x03: SetTimeZero,
}