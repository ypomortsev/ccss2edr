import time
import struct
import dataclasses
from dataclasses import dataclass

TECH = {
    # Should match mapping in ArgyllCMS spectro/oemarch.c, parse_EDR
    0: 'Color Matching Function',
    1: 'Custom',
    2: 'CRT',
    3: 'LCD CCFL IPS',
    4: 'LCD CCFL VPA',
    5: 'LCD CCFL TFT',
    6: 'LCD CCFL Wide Gamut IPS',
    7: 'LCD CCFL Wide Gamut VPA',
    8: 'LCD CCFL Wide Gamut TFT',
    9: 'LCD White LED IPS',
    10: 'LCD White LED VPA',
    11: 'LCD White LED TFT',
    12: 'LCD RGB LED IPS',
    13: 'LCD RGB LED VPA',
    14: 'LCD RGB LED TFT',
    15: 'LED OLED',
    16: 'LED AMOLED',
    17: 'Plasma',
    18: 'LCD RG Phosphor',
    19: 'Projector RGB Filter Wheel',
    20: 'Projector RGBW Filter Wheel',
    21: 'Projector RGBCMY Filter Wheel',
    22: 'Projector',
    23: 'LCD PFS Phosphor',
    24: 'LED WOLED',
    64: 'LCD GB-R Phosphor IPS'
}

TECH_STRINGS_TO_INDEX = {v: k for k, v in TECH.items()}


class StructMeta(type):

    def __init__(cls, name, bases, d):
        if dataclasses.is_dataclass(d):
            raise ValueError("Class {} is not a dataclass".format(name))
        if 'struct' not in d:
            raise ValueError("Class {} doesn't define struct".format(name))
        type.__init__(cls, name, bases, d)


class Struct:
    __metaclass__ = StructMeta
    struct = None

    def pack(self):
        return self.struct.pack(*dataclasses.astuple(self))

    def pack_into(self, buffer, offset):
        return self.struct.pack_into(buffer, offset,
                                     *dataclasses.astuple(self))

    @classmethod
    def unpack(cls, string):
        return cls(*cls.struct.unpack(string))

    @classmethod
    def unpack_from(cls, buffer, offset=0):
        return cls(*cls.struct.unpack_from(buffer, offset))


@dataclass
class EDRHeader(Struct):
    magic: bytes = b'EDR DATA1'
    unknown_0x10: int = 1
    unknown_0x14: int = 1
    creation_time: int = int(time.time())
    creation_tool: bytes = b'ccss2edr'
    display_description: bytes = b''
    tech_type: int = 1
    num_sets: int = 0
    display_manufacturer: bytes = b''
    display_manufacturer_id: bytes = b''
    display_model: bytes = b''
    unknown_0x228: int = 0
    unknown_0x22c: int = 1
    has_spectral_data: int = 1
    spectral_start_nm: float = 0.0
    spectral_end_nm: float = 0.0
    spectral_norm: float = 0.0
    unknown_0x248: int = 0

    struct = struct.Struct(
        '< 9s7x I I Q 64s 256s I I 64s 64s 64s I H H d d d I 12x')


@dataclass
class EDRDisplayDataHeader(Struct):
    magic: bytes = b'DISPLAY DATA'
    RGB_r: int = 255  # 0-255
    RGB_g: int = 255  # 0-255
    RGB_b: int = 255  # 0-255
    type: bytes = b'c'  # either 'c' or 'x'
    unknown_0x58: float = 0.0
    Yxy_Y: float = 0.0  # these actually seem to be XYZ, at least in some edrs
    Yxy_x: float = 0.0
    Yxy_y: float = 0.0
    Yxy_z_internal: float = 0.0  # gets set to zero when edr is read?

    struct = struct.Struct('< 12s68x HHH 2s d dddd')


@dataclass
class EDRSpectralDataHeader(Struct):
    magic: bytes = b'SPECTRAL DATA'
    num_samples: int = 0
    unknown_0x20: int = 0
    unknown_0x24: bytes = b'0000'

    struct = struct.Struct('< 13s3x I I 4s')
