#!/usr/bin/env python
import argparse
import locale
import time
import struct
from array import array
from .cgats import CGATS
from .edr import (
    EDRHeaderFactory,
    EDRDisplayDataHeaderFactory,
    EDRSpectralDataHeaderFactory,
    TECH_STRINGS
)


def main():
    parser = argparse.ArgumentParser(
        description='Convert a .ccss file to .edr')

    parser.add_argument('ccss',
                        type=argparse.FileType('r'),
                        help='.ccss input filename')
    """
    parser.add_argument('--ti',
                        type=argparse.FileType('r'),
                        help='.ti1/.ti3 filename')
    """
    parser.add_argument('--tech-type',
                        type=int,
                        help='technology type')
    parser.add_argument('out',
                        type=argparse.FileType('wb'),
                        help='.edr output filename')

    args = parser.parse_args()

    ccss = CGATS(args.ccss)

    # EDR DATA header

    edr_header = EDRHeaderFactory.new()

    edr_header.creation_tool = 'ccss2edr'

    if 'DESCRIPTOR' in ccss and ccss['DESCRIPTOR'] != 'Not specified':
        edr_header.display_description = ccss['DESCRIPTOR']
    elif 'DISPLAY' in ccss:
        edr_header.display_description = ccss['DISPLAY']
    if 'ORIGINATOR' in ccss:
        edr_header.creation_tool += ' ({})'.format(ccss['ORIGINATOR'])
    if 'CREATED' in ccss:
        edr_header.creation_time = time.mktime(unasctime(ccss['CREATED']))
    if 'MANUFACTURER_ID' in ccss:
        edr_header.display_manufacturer_id = ccss['MANUFACTURER_ID']
    if 'MANUFACTURER' in ccss:
        edr_header.display_manufacturer = ccss['MANUFACTURER']
    if args.tech_type:
        edr_header.tech_type = args.tech_type
    elif 'TECHNOLOGY' in ccss:
        if ccss['TECHNOLOGY'] in TECH_STRINGS:
            edr_header.tech_type = TECH_STRINGS.index(ccss['TECHNOLOGY'])
        else:
            print('Warning: Unknown technology %r' % ccss['TECHNOLOGY'])

    edr_header.spectral_start_nm = float(ccss['SPECTRAL_START_NM'])
    edr_header.spectral_end_nm = float(ccss['SPECTRAL_END_NM'])
    edr_header.spectral_space = (edr_header.spectral_end_nm -
                                 edr_header.spectral_start_nm) / (
                                     int(ccss['SPECTRAL_BANDS']) - 1)

    edr_header.num_sets = int(ccss['NUMBER_OF_SETS'])

    args.out.write(EDRHeaderFactory.pack(edr_header))

    for set_num in range(edr_header.num_sets):
        display_data_header = EDRDisplayDataHeaderFactory.new()
        # TODO?
        args.out.write(EDRDisplayDataHeaderFactory.pack(display_data_header))

        spectral_data_header = EDRSpectralDataHeaderFactory.new()
        spectral_data_header.num_samples = int(ccss['SPECTRAL_BANDS'])
        args.out.write(EDRSpectralDataHeaderFactory.pack(spectral_data_header))

        # strip leading SAMPLE_ID and convert from mW/nm/m^2 to W/nm/m^2
        data = [float(val) / 1000.0 for val in ccss.data[set_num][1:]]
	for spectral_measurment_data in data:
	    args.out.write(struct.pack('<d',spectral_measurment_data))


def unasctime(timestr):
    loc = locale.getlocale()
    locale.setlocale(locale.LC_TIME, 'C')

    st = time.strptime(timestr)

    locale.setlocale(locale.LC_TIME, loc)

    return st


if __name__ == '__main__':
    main()
