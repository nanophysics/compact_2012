#
# Double click this file to create empty files for Compact_2012 which is defined in calib_serial.
# Run this script on the SDCARD
#
# Existing files will NOT be OVERWRITTEN!
#
import os

import config_serial
import calib_prepare_lib
import micropython_portable

DACS_COUNT=10

for iDacA_index in range(0, micropython_portable.DACS_COUNT, 2):
  for iFileNumber in range(0, 16):
    filename = 'calib_raw_{}_dac{}-{}.txt'.format(config_serial.SERIAL, iDacA_index, iFileNumber)
    if os.path.exists(filename):
      # Don't override existing files
      print('{} skipped'.format(filename))
      continue
    with open(filename, 'w') as f:
      print('{} created'.format(filename))
