#!/usr/bin/env python
import argparse
from array import array
from .edr import (
    EDRHeaderFactory,
    EDRDisplayDataHeaderFactory,
    EDRSpectralDataHeaderFactory
)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Print .edr file')

    parser.add_argument('edr',
                        type=argparse.FileType('rb'),
                        help='.edr input filename')

    return parser.parse_args()


def main():
    args = parse_args()

    print('EDR Header:')
    edr_header = args.edr.read(EDRHeaderFactory.struct.size)
    edr_tup = EDRHeaderFactory.unpack_from(edr_header)
    print_named_tuple(edr_tup, level=1)

    for set_num in range(1, edr_tup.num_sets + 1):
        print('Set {}'.format(set_num))
        print('\tDisplay Data Header:')

        edr_header = args.edr.read(EDRDisplayDataHeaderFactory.struct.size)
        edr_tup = EDRDisplayDataHeaderFactory.unpack_from(edr_header)
        print_named_tuple(edr_tup, level=2)

        print('\tSpectral Data Header:')

        spec_header = args.edr.read(EDRSpectralDataHeaderFactory.struct.size)
        spec_tup = EDRSpectralDataHeaderFactory.unpack_from(spec_header)
        print_named_tuple(spec_tup, level=2)

        spec_data = args.edr.read(8 * spec_tup.num_samples)  # array of doubles
        spec_data_arr = array('d', spec_data)

        print('\tSpectral Data: {!s}'.format(spec_data_arr.tolist()))


def print_named_tuple(tup, level=0):
    for attr in tup.__slots__:
        print('{}{}: {!r}'.format('\t' * level, attr, getattr(tup, attr)))

if __name__ == '__main__':
    main()
