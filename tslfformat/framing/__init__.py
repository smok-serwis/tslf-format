# coding=UTF-8
"""
Reading and writing TSLF records.
"""
from __future__ import print_function, absolute_import, division
import six
import logging
import struct

from tslfformat.framing.shortcodes import ShortCodeDatabase, ShortCodeType

logger = logging.getLogger(__name__)


HEADER = b'TSLFFORMAT00'

__all__ = ('HEADER', 'ValueStatus', 'TimeUnit', 'BaseSegment',
           'Bits8ShortCodeValue', 'Bits16ShortCodeValue', 'Bits32ShortCodeValue', 'PathValue',
           'Bits8ShortCodeDefinition', 'Bits16ShortCodeDefinition', 'Bits32ShortCodeDefinition',
           'ConsiderSyncedUntil', 'SetTimeZero',
           'SEGMENT_TYPE_TO_CLASS'
           )



class ValueStatus(object):
    OK = 0b00
    MALFORMED = 0b01
    TIMEOUT = 0b10
    INVALID = 0b11

class TimeUnit(object):
    MILLISECONDS = 0
    SECONDS = 1


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



class PathValue(BaseSegment):
    """0x04-0x07"""

    SHORT_CODE_BITNESS = None
    SHORT_CODE_LENGTH = None
    SHORT_CODE_TYPE = None
    SEGMENT_CODE = None

    def __init__(self, sc_type, sc, timestamp, time_unit, value_status, value):
        """
        :param timestamp: any length - will be fitted to smallest datatype possible.
                          not known if
        :type value: binary
        """
        self.sc_type = sc_type
        self.sc = sc
        self.timestamp = timestamp
        self.value_status = value_status
        self.value = value
        self.time_unit = time_unit

    def write_to(self, f):
        segtype = {ShortCodeType.BITS_8: 0x04,
                   ShortCodeType.BITS_16: 0x05,
                   ShortCodeType.BITS_32: 0x06}[self.sc_type]

        descriptor = 0

        # timestamp value
        if self.timestamp <= 0xFFFF:
            descriptor |= 0b10
            tt = '!H'
        elif self.timestamp <= 0xFFFFFF:
            descriptor |= 0b01
            tt = None   # code for 24 bit
        elif self.timestamp <= 0xFFFFFFFF:
            tt = '!L'
        else:
            descriptor |= 0b11
            tt = '!Q'

        # timestamp type
        if self.time_unit == TimeUnit.SECONDS:
            descriptor |= 0b100

        # value status
        descriptor |= {
            ValueStatus.OK: 0,
            ValueStatus.INVALID: 0b11000,
            ValueStatus.MALFORMED: 0b01000,
            ValueStatus.TIMEOUT: 0b10000
        }[self.value_status]

        # value length coding
        if len(self.value) == 0:
            descriptor |= 0
            vc = None
        elif len(self.value) == 1:
            descriptor |= 0b10000000
            vc = None
        elif len(self.value) == 2:
            descriptor |= 0b10100000
            vc = None
        elif len(self.value) == 4:
            descriptor |= 0b11000000
            vc = None
        elif len(self.value) == 8:
            descriptor |= 0b11100000
            vc = None
        elif len(self.value) <= 0xFF:
            descriptor |= 0b00100000
            vc = '!B'
        elif len(self.value) <= 0xFFFF:
            descriptor |= 0b01000000
            vc = '!H'
        elif len(self.value) <= 0xFFFFFFFF:
            descriptor |= 0b01100000
            vc = '!L'
        else:
            raise ValueError('what?')


        # roll
        f.write(struct.pack('!B', descriptor))

        if tt is None:  # 24 bits
            f.write(struct.pack('!L', self.timestamp))[1:]
        else:
            f.write(struct.pack(tt, self.timestamp))

        f.write(struct.pack({
            ShortCodeType.BITS_8: '!B',
            ShortCodeType.BITS_16: '!H',
            ShortCodeType.BITS_32: '!L',
        }[self.sc_type], self.sc))

        if vc is not None:
            f.write(struct.pack(vc, len(self.value)))

        f.write(self.value)

    @classmethod
    def read_from(cls, f):
        desc, = struct.unpack('!B', f.read(1))

        tt_struct, tt_len = {
            0b00: ('!L', 4),
            0b01: (None, 3),    # 24 bit
            0b10: ('!H', 2),
            0b11: ('!Q', 8)
        }[desc & 0b11]

        value_status = {
            0b00000: ValueStatus.OK,
            0b01000: ValueStatus.MALFORMED,
            0b10000: ValueStatus.TIMEOUT,
            0b11000: ValueStatus.INVALID,
        }[desc & 0b11000]

        time_unit = {
            0b000: TimeUnit.MILLISECONDS,
            0b100: TimeUnit.SECONDS
        }[desc & 0b100]

        vc_struct, vc_len, value_length = {
            0b00000000: (None, 0, 0),
            0b00100000: ('!B', 1, None),
            0b01000000: ('!H', 2, None),
            0b01100000: ('!L', 4, None),
            0b10000000: (None, 0, 1),
            0b10100000: (None, 0, 2),
            0b11000000: (None, 0, 4),
            0b11100000: (None, 0, 8),
        }[desc & 0b11100000]

        t_data = f.read(tt_len)

        if tt_struct is None:
            t_data = b'\x00' + t_data
            tt_struct = '!L'

        timestamp, = struct.unpack(tt_struct, t_data)

        sc, = struct.unpack(cls.SHORT_CODE_BITNESS, f.read(cls.SHORT_CODE_LENGTH))

        if value_length is None:
            value_length, = struct.unpack(vc_struct, f.read(vc_len))

        value = f.read(value_length)

        return PathValue(cls.SHORT_CODE_TYPE, sc, timestamp, time_unit, value_status, value)



class Bits8ShortCodeValue(PathValue):
    SHORT_CODE_BITNESS = '!B'
    SHORT_CODE_LENGTH = 1
    SHORT_CODE_TYPE = ShortCodeType.BITS_8
    SEGMENT_CODE = 0x04

class Bits16ShortCodeValue(PathValue):
    SHORT_CODE_BITNESS = '!H'
    SHORT_CODE_LENGTH = 2
    SHORT_CODE_TYPE = ShortCodeType.BITS_16
    SEGMENT_CODE = 0x05

class Bits32ShortCodeValue(PathValue):
    SHORT_CODE_BITNESS = '!L'
    SHORT_CODE_LENGTH = 4
    SHORT_CODE_TYPE = ShortCodeType.BITS_32
    SEGMENT_CODE = 0x06



SEGMENT_TYPE_TO_CLASS = {
    0x00: Bits8ShortCodeDefinition,
    0x01: Bits16ShortCodeDefinition,
    0x02: Bits32ShortCodeDefinition,
    0x03: SetTimeZero,
    0x04: Bits8ShortCodeValue,
    0x05: Bits16ShortCodeValue,
    0x06: Bits32ShortCodeValue,

    0x08: ConsiderSyncedUntil
}