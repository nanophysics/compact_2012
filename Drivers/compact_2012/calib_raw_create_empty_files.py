import os

import calib_prepare_lib
import micropython_portable

SERIAL='20190606_01'

DACS_COUNT=10

for iDacA_index in range(0, micropython_portable.DACS_COUNT, 2):
  for iFileNumber in range(0, 16):
    filename = 'calib_raw_{}_dac{}-{}.txt'.format(SERIAL, iDacA_index, iFileNumber)
    filenameFull = os.path.join(calib_prepare_lib.DIRECTORY_CALIBRATION_RAW_FULL, filename)
    if os.path.exists(filenameFull):
      # Don't override existing files
      print('{} skipped'.format(filename))
      continue
    with open(filenameFull, 'w') as f:
      print('{} created'.format(filename))
