#!/usr/bin/env python3
import argparse
import dataclasses
from array import array
from .edr import (EDRHeader, EDRDisplayDataHeader, EDRSpectralDataHeader)


def parse_args():
    parser = argparse.ArgumentParser(description='Print .edr file')

    parser.add_argument('edr',
                        type=argparse.FileType('rb'),
                        help='.edr input filename')

    return parser.parse_args()


def main():
    args = parse_args()

    print('EDR Header:')
    edr_header = EDRHeader.unpack_from(args.edr.read(EDRHeader.struct.size))
    print_dataclass(edr_header, indent=1)

    for set_num in range(1, edr_header.num_sets + 1):
        print('Set {}'.format(set_num))
        print('\tDisplay Data Header:')

        edr_header = EDRDisplayDataHeader.unpack_from(
            args.edr.read(EDRDisplayDataHeader.struct.size))
        print_dataclass(edr_header, indent=2)

        print('\tSpectral Data Header:')

        spec_header = EDRSpectralDataHeader.unpack_from(
            args.edr.read(EDRSpectralDataHeader.struct.size))
        print_dataclass(spec_header, indent=2)

        spec_data = args.edr.read(8 *
                                  spec_header.num_samples)  # array of doubles
        spec_data_arr = array('d', spec_data)

        print('\tSpectral Data: {!s}'.format(spec_data_arr.tolist()))


def print_dataclass(obj, indent=0):
    for field in dataclasses.fields(obj):
        print('{}{}: {!r}'.format('\t' * indent, field.name,
                                  getattr(obj, field.name)))


if __name__ == '__main__':
    main()
