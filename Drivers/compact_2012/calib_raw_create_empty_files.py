#
# Double click this file to create empty files for Compact_2012 which is defined in calib_serial.
# Run this script on the SDCARD
#
# Existing files will NOT be OVERWRITTEN!
#
import os

import config_serial
import micropython_portable

DACS_COUNT = 10
CALIB_FILES_PER_DAC = 32
FILENAME_CALIB_RAW_TEMPLATE = 'calib_raw_{}_dac{}-{:02d}.txt'

for iDacA_index in range(0, micropython_portable.DACS_COUNT, 2):
  for iFileNumber in range(0, CALIB_FILES_PER_DAC):
    filename = FILENAME_CALIB_RAW_TEMPLATE.format(config_serial.SERIAL, iDacA_index, iFileNumber)
    if os.path.exists(filename):
      # Don't override existing files
      print('{} skipped'.format(filename))
      continue
    with open(filename, 'w') as f:
      print('{} created'.format(filename))
