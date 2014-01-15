import time
import struct
from record import recordtype


TECH_STRINGS = [
    'Color Matching Function',
    'Custom',
    'CRT',
    'LCD CCFL IPS',
    'LCD CCFL VPA',
    'LCD CCFL TFT',
    'LCD CCFL Wide Gamut IPS',
    'LCD CCFL Wide Gamut VPA',
    'LCD CCFL Wide Gamut TFT',
    'LCD White LED IPS',
    'LCD White LED VPA',
    'LCD White LED TFT',
    'LCD RGB LED IPS',
    'LCD RGB LED VPA',
    'LCD RGB LED TFT',
    'LED OLED',
    'LED AMOLED',
    'Plasma',
    'LCD RG Phosphor',
    'Projector RGB Filter Wheel',
    'Projector RGBW Filter Wheel',
    'Projector RGBCMY Filter Wheel',
    'Projector',
    'Unknown'
]


class StructFactoryMeta(type):
    def __init__(cls, name, bases, d):
        if 'record_class' not in d:
            raise ValueError("Class %s doesn't define record_class" % name)
        if 'defaults' not in d:
            raise ValueError("Class %s doesn't define defaults" % name)
        if 'struct' not in d:
            raise ValueError("Class %s doesn't define struct" % name)
        type.__init__(cls, name, bases, d)


class StructFactory(object):
    __metaclass__ = StructFactoryMeta
    record_class = None
    defaults = None
    struct = None

    @classmethod
    def new(cls, values=None):
        if values is None:
            values = cls.defaults
        return cls.record_class(*values)

    @classmethod
    def pack(cls, struct_tuple):
        return cls.struct.pack(*struct_tuple)

    @classmethod
    def pack_into(cls, buffer, offset, struct_tuple):
        return cls.struct.pack_into(buffer, offset, *struct_tuple)

    @classmethod
    def unpack(cls, string):
        return cls.new(cls.struct.unpack(string))

    @classmethod
    def unpack_from(cls, buffer, offset=0):
        return cls.new(cls.struct.unpack_from(buffer, offset))


class EDRHeaderFactory(StructFactory):
    record_class = recordtype('EDRHeader', [
        'magic',
        'unknown_0x10',
        'unknown_0x14',
        'creation_time',
        'creation_tool',
        'display_description',
        'tech_type',
        'num_sets',
        'display_manufacturer',
        'display_manufacturer_id',
        'display_model',
        'unknown_0x228',
        'unknown_0x22c',
        'has_spectral_data',
        'spectral_start_nm',
        'spectral_end_nm',
        'spectral_space',
        'unknown_0x248'
    ])
    defaults = (
        'EDR DATA1',
        1,
        1,
        int(time.time()),
        'edr.py',
        '',
        1,
        0,
        '',
        '',
        '',
        0,
        1,
        1,
        0.0,
        0.0,
        0.0,
        0
    )
    struct = struct.Struct(
        '< 9s7x I I Q 64s 256s I I 64s 64s 64s I H H d d d I 12x')


class EDRDisplayDataHeaderFactory(StructFactory):
    record_class = recordtype('EDRDisplayDataHeader', [
        'magic',
        'RGB_r',  # 0-255
        'RGB_g',  # 0-255
        'RGB_b',  # 0-255
        'type',   # either 'c' or 'x'
        'unknown_0x58',
        'Yxy_Y',  # these actually seem to be XYZ, at least in some edrs
        'Yxy_x',
        'Yxy_y',
        'Yxy_z_internal'  # gets set to zero when edr is read?
    ])
    defaults = (
        'DISPLAY DATA',
        255,
        255,
        255,
        'c',
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
    )
    struct = struct.Struct('< 12s68x HHH 2s d dddd')


class EDRSpectralDataHeaderFactory(StructFactory):
    record_class = recordtype('EDRSpectralDataHeader', [
        'magic',
        'num_samples',
        'unknown_0x20',
        'unknown_0x24'
    ])
    defaults = (
        'SPECTRAL DATA',
        0,
        0,
        '0000'
    )
    struct = struct.Struct('< 13s3x I I 4s')
