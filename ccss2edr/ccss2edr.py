#!/usr/bin/env python3
import argparse
import locale
import struct
import time
from dataclasses import dataclass
from .cgats import CGATS
from .edr import (
    EDRHeader,
    EDRDisplayDataHeader,
    EDRSpectralDataHeader,
    TECH_STRINGS_TO_INDEX,
)


@dataclass
class SpectralData:
    # Wavelength of the first spectral band, in nanometers
    start_nm: float
    # Wavelength of the last spectral band, in nanometers
    end_nm: float
    # Width of each spectral band, in nanometers
    space_nm: float
    # Spectral norm
    norm: float
    # Number of samples in each spectral data set
    num_bands: int
    # Number of spectral data sets
    num_sets: int
    # Sets of spectral data
    sets: list[list[float]]

    @staticmethod
    def from_ccss(ccss: CGATS):
        num_bands = int(ccss["SPECTRAL_BANDS"])
        start_nm = float(ccss["SPECTRAL_START_NM"])
        end_nm = float(ccss["SPECTRAL_END_NM"])
        norm = float(ccss["SPECTRAL_NORM"])
        space_nm = (end_nm - start_nm) / (num_bands - 1)

        # Always skip the first field, SAMPLE_ID
        skip_fields = 1

        if start_nm > 380.0:
            raise Exception(
                "spectral data start must be <= 380.0 nm, is {}".format(
                    start_nm))
        elif start_nm < 380.0:
            skip_samples = int((380.0 - start_nm) / space_nm)
            # Skip bands so the data starts at 380 nm
            skip_fields += skip_samples
            num_bands -= skip_samples
            start_nm = 380.0
            print("Warning: spectral data does not start at 380 nm, "
                  "skipping {} leading bands".format(skip_samples))

        num_sets = int(ccss["NUMBER_OF_SETS"])

        sets = []
        for data in ccss.data:
            sets.append([
                # convert from mW/nm/m^2 to W/nm/m^2
                float(val) / 1000.0 for val in data[skip_fields:]
            ])

        return SpectralData(start_nm, end_nm, space_nm, norm, num_bands,
                            num_sets, sets)

    def edr_spectral_data_header(self):
        header = EDRSpectralDataHeader()
        header.num_samples = self.num_bands
        return header


def main():
    parser = argparse.ArgumentParser(
        description="Convert a .ccss file to .edr")

    parser.add_argument("ccss",
                        type=argparse.FileType("r"),
                        help=".ccss input filename")
    parser.add_argument("--tech-type", type=int, help="technology type")
    parser.add_argument("out",
                        type=argparse.FileType("wb"),
                        help=".edr output filename")

    args = parser.parse_args()

    ccss = CGATS(args.ccss)

    # EDR DATA header

    edr_header = EDRHeader()

    if "DESCRIPTOR" in ccss and ccss["DESCRIPTOR"] != "Not specified":
        edr_header.display_description = ccss["DESCRIPTOR"].encode()
    elif "DISPLAY" in ccss:
        edr_header.display_description = ccss["DISPLAY"].encode()
    if "ORIGINATOR" in ccss:
        edr_header.creation_tool += " ({})".format(ccss["ORIGINATOR"]).encode()
    if "CREATED" in ccss:
        edr_header.creation_time = int(time.mktime(unasctime(ccss["CREATED"])))
    if "MANUFACTURER_ID" in ccss:
        edr_header.display_manufacturer_id = ccss["MANUFACTURER_ID"].encode()
    if "MANUFACTURER" in ccss:
        edr_header.display_manufacturer = ccss["MANUFACTURER"].encode()
    if args.tech_type:
        edr_header.tech_type = args.tech_type
    elif "TECHNOLOGY" in ccss:
        tech = ccss["TECHNOLOGY"]
        if tech not in TECH_STRINGS_TO_INDEX and tech[-4:] in (" IPS", " VPA",
                                                               " TFT"):
            tech = tech[:-4]
        if tech in TECH_STRINGS_TO_INDEX:
            edr_header.tech_type = TECH_STRINGS_TO_INDEX[tech]
        else:
            print("Warning: Unknown technology %r" % tech)

    spectral_data = SpectralData.from_ccss(ccss)

    edr_header.spectral_start_nm = spectral_data.start_nm
    edr_header.spectral_end_nm = spectral_data.end_nm
    edr_header.spectral_norm = spectral_data.norm
    edr_header.num_sets = spectral_data.num_sets

    args.out.write(edr_header.pack())

    display_data_header = EDRDisplayDataHeader()
    spectral_data_header = spectral_data.edr_spectral_data_header()

    for spectral_set in spectral_data.sets:
        args.out.write(display_data_header.pack())
        args.out.write(spectral_data_header.pack())

        for val in spectral_set:
            args.out.write(struct.pack("<d", val))


def unasctime(timestr):
    loc = locale.getlocale()
    locale.setlocale(locale.LC_TIME, "C")

    st = time.strptime(timestr)

    locale.setlocale(locale.LC_TIME, loc)

    return st


if __name__ == "__main__":
    main()
