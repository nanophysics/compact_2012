# Compact2012

## DAC

## Calibration Extension

This extensions may be assembled on the XY-BCP.
The software used to use this extensions uses the prefix `calib_`.

## Workflow

### `calib_raw_`: Measure the DAC

- Write Program onto SD-Card:
  - Copy these files from this directory to the sdcard:
    - main.py
    - config_serial.py
    - micropython_portable
    - micropython_logic
    - micropython_ads1219
  - Copy `config_serial_template.py` to `config_serial.py`.
  - Make sure the serial number of `config_serial.py` pyboard corresponds to the Compact_2012
- Power on first Compact_2012, then the pyboard.
  - Green LED blinks: Measuring
  - Green LED steady: Done
  - Red LED: Error

- Wait for "Green LED steady'.
- Remove SD-Card and copy file to TODO

### `calib_prepare_`: Run calibration algorithmus

- Place files into folder TODO
- Run `calib_prepare_run.py`
- Move resultig files into folder TODO and add them to git.
- Run `calib_correction_test_endtest.py`.
- Take `calib_correction_test_endtest_out.txt` and update OpenOffice Calc TODO and verify result.
- Trash `calib_raw_`-files.

### `calib_correction_`: Apply calibration data

- Delete all files from pyboards flashdrive.
- Copy `config_serial_template.py` to `config_serial.py`.
- Make sure the serial number of `config_serial.py` pyboard corresponds to the Compact_2012

