#!/usr/bin/env python3
import argparse
import locale
import time
import struct
from .cgats import CGATS
from .edr import (EDRHeader, EDRDisplayDataHeader, EDRSpectralDataHeader,
                  TECH_STRINGS_TO_INDEX)


def main():
    parser = argparse.ArgumentParser(
        description='Convert a .ccss file to .edr')

    parser.add_argument('ccss',
                        type=argparse.FileType('r'),
                        help='.ccss input filename')
    parser.add_argument('--tech-type', type=int, help='technology type')
    parser.add_argument('out',
                        type=argparse.FileType('wb'),
                        help='.edr output filename')

    args = parser.parse_args()

    ccss = CGATS(args.ccss)

    # EDR DATA header

    edr_header = EDRHeader()

    if 'DESCRIPTOR' in ccss and ccss['DESCRIPTOR'] != 'Not specified':
        edr_header.display_description = ccss['DESCRIPTOR'].encode()
    elif 'DISPLAY' in ccss:
        edr_header.display_description = ccss['DISPLAY'].encode()
    if 'ORIGINATOR' in ccss:
        edr_header.creation_tool += ' ({})'.format(ccss['ORIGINATOR']).encode()
    if 'CREATED' in ccss:
        edr_header.creation_time = int(time.mktime(unasctime(ccss['CREATED'])))
    if 'MANUFACTURER_ID' in ccss:
        edr_header.display_manufacturer_id = ccss['MANUFACTURER_ID'].encode()
    if 'MANUFACTURER' in ccss:
        edr_header.display_manufacturer = ccss['MANUFACTURER'].encode()
    if args.tech_type:
        edr_header.tech_type = args.tech_type
    elif 'TECHNOLOGY' in ccss:
        tech = ccss['TECHNOLOGY']
        if (tech not in TECH_STRINGS_TO_INDEX
                and tech[-4:] in (" IPS", " VPA", " TFT")):
            tech = tech[:-4]
        if tech in TECH_STRINGS_TO_INDEX:
            edr_header.tech_type = TECH_STRINGS_TO_INDEX[tech]
        else:
            print('Warning: Unknown technology %r' % tech)

    edr_header.spectral_start_nm = float(ccss['SPECTRAL_START_NM'])
    edr_header.spectral_end_nm = float(ccss['SPECTRAL_END_NM'])
    edr_header.spectral_norm = float(ccss['SPECTRAL_NORM'])

    edr_header.num_sets = int(ccss['NUMBER_OF_SETS'])

    args.out.write(edr_header.pack())

    for set_num in range(edr_header.num_sets):
        display_data_header = EDRDisplayDataHeader()
        # TODO?
        args.out.write(display_data_header.pack())

        spectral_data_header = EDRSpectralDataHeader()
        spectral_data_header.num_samples = int(ccss['SPECTRAL_BANDS'])
        args.out.write(spectral_data_header.pack())

        # strip leading SAMPLE_ID and convert from mW/nm/m^2 to W/nm/m^2
        spectral_measurement_data = [
            float(val) / 1000.0 for val in ccss.data[set_num][1:]
        ]

        for val in spectral_measurement_data:
            args.out.write(struct.pack('<d', val))


def unasctime(timestr):
    loc = locale.getlocale()
    locale.setlocale(locale.LC_TIME, 'C')

    st = time.strptime(timestr)

    locale.setlocale(locale.LC_TIME, loc)

    return st


if __name__ == '__main__':
    main()
