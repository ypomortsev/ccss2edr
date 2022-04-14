# ccss2edr

This tool converts Argyll .ccss (Colorimeter Calibration Spectral Set) files to the X-Rite
.edr format. The motivation is to possibly get more accurate color calibration with the Dell
UltraSharp Color Calibration Solution by feeding it a more accurate backlight spectrum profile
instead of a generic W-LED or RG-LED profile.

## Usage

1. Install Python 3.9+
2. Install [Poetry](https://python-poetry.org/docs/#installation)
3. Run `poetry install`
4. Run `poetry run ccss2edr in.ccss out.edr` to convert the CCSS file `in.ccss`
   in the current working directory to `out.edr`
