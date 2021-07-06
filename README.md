# ccss2edr

This tool converts Argyll .ccss (Colorimeter Calibration Spectral Set) files to the X-Rite
.edr format. The motivation is to possibly get more accurate color calibration with the Dell
UltraSharp Color Calibration Solution by feeding it a more accurate backlight spectrum profile
instead of a generic W-LED or RG-LED profile.

## Usage

1. Install Python 3.9
2. Install [pipenv](https://pipenv-fork.readthedocs.io/en/latest/index.html)
3. Run `pipenv run ccss2edr in.ccss out.edr`
