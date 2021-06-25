#
# Compact_2012
#
# Measure the DAC's of Compact_2012 and store
# the result in 'calib_raw_'-files.
#


import uos
import utime
print('This is "main.py". uos.getcwd()="{}"'.format(uos.getcwd()))

import config_identification

firmware_version = uos.uname().release
print('firmware_version:', firmware_version)
firmware_required = '1.14.0'
if firmware_version != firmware_required:
    raise Exception('firmware is {} but {} is required!'.format(firmware_version, firmware_required))

for filename in ('config_identification.py', 'micropython_ads1219.py', 'micropython_portable.py', 'micropython_logic.py'):
  print('execfile("{}")'.format(filename))
  execfile(filename)

CALIB_FILES_PER_DAC = 32
FILENAME_TMP = 'tmp.txt'
FILENAME_CALIB_RAW_TEMPLATE = 'calib_raw_{}_dac{}-{:02d}.txt'
FILENAME_CALIB_RAW_TEMPLATE_DAC12 = 'calib_raw_{}_gain_DAC12.txt'

try:
  timer_blink.callback(None)

  calib_raw_init()

  # 650h: Total
  # 50h: Pro DAC
  # 3h: Pro File (16 File for every DAC)
  iDacFileSize = DAC20_MAX//CALIB_FILES_PER_DAC
  # Show progress every 10%
  iDacProgress = iDacFileSize//10
  # iDacFileSize = 100

  list_files = uos.listdir()

  # Measure DAC12 gain
  filename = FILENAME_CALIB_RAW_TEMPLATE_DAC12.format(HWSERIAL)
  if filename in list_files:
    print('{} exists. Skipped'.format(filename))
  else:
    print('{} measureing...'.format(filename))
    calib_set_DAC12(iDAC12_index=0, iDAC12_value=0)
    utime.sleep(3.0)
  
    I_SETTLE_TIME_DAC12_S = 0.1
    I_MEASUREMENT_COUNT_DAC12 = 20
    with open(FILENAME_TMP, 'w') as f:
      for iDAC_index in range(DACS_COUNT):
        calib_set_mux(iDAC_index)

        for iMeasurement in range(I_MEASUREMENT_COUNT_DAC12):
          if iMeasurement%4 == 0:
            p_LED_GREEN_out.on()
          else:
            p_LED_GREEN_out.off()
          for iDAC12_value in (0, DAC12_MAX-1):
            # Set DAC12
            calib_set_DAC12(iDAC_index, iDAC12_value)
            utime.sleep(I_SETTLE_TIME_DAC12_S)

            # Read from ADC24
            iADC24_signed = adc.read_data_signed()
            f.write('{}\t{}\t{}\n'.format(iDAC_index, iDAC12_value, iADC24_signed))


    uos.rename(FILENAME_TMP, filename)


  # Measure DAC20 steps (very slow)
  SETTLE_TIME_S = 10
  iSettleTime_s = SETTLE_TIME_S

  for iDacA_index in range(0, DACS_COUNT, 2):
    for iFileNum in range(CALIB_FILES_PER_DAC):
      iDacStart = iFileNum*iDacFileSize
      # iDacA_index = 0
      # iDacStart=0x80000
      # iDacEnd=0x80000+100
      # iDacEnd=0xFFFFF
      filename = FILENAME_CALIB_RAW_TEMPLATE.format(HWSERIAL, iDacA_index, iDacStart//iDacFileSize)
      if filename in list_files:
        print('{} exists. Skipped'.format(filename))
        iSettleTime_s = SETTLE_TIME_S
        continue

      def status(iDac):
        '''
          Show progess on green blinking led and "filename.txt 52%"
        '''
        if iDac%4 == 0:
          p_LED_GREEN_out.on()
        else:
          p_LED_GREEN_out.off()
        if iDac%iDacProgress == 5:
          iDacProgess = iDac-iDacStart
          fPercent = iDacProgess/iDacFileSize
          fPercentRemaining = 1.0-fPercent
          fTimePerMeasurement_ms = (utime.ticks_ms()-time_start_ms)/iDacProgess
          fTimeRemaining_ms = (iDacEnd-iDac)*fTimePerMeasurement_ms
          iTotalMeasurementsRemaining = DAC20_MAX*(DACS_COUNT-iDacA_index-2)//2 + DAC20_MAX-iDac
          fTimeTotalRemaining_ms = iTotalMeasurementsRemaining * fTimePerMeasurement_ms
          print('{}: {:0.0f}% {:0.1f}h remaining for this file. {:0.1f}h remaining total.'.format(
              filename, 
              100.0*fPercentRemaining,
              fTimeRemaining_ms/1000.0/60.0/60.0,
              fTimeTotalRemaining_ms/1000.0/60.0/60.0
          ))

      time_start_ms = utime.ticks_ms() + 1000*iSettleTime_s
      iDacEnd = iDacStart+iDacFileSize
      calib_raw_measure(FILENAME_TMP, HWSERIAL, iDacA_index, iDacStart, iDacEnd, iSettleTime_s=iSettleTime_s, f_status=status)
      uos.rename(FILENAME_TMP, filename)
      print('{}: {}%'.format(filename, 100))
      iSettleTime_s = 0

  p_LED_GREEN_out.on()
  print('DONE: success!')

# except KeyboardInterrupt:
#   pyb_led_red.on()
#   print('KeyboardInterrupt! machine.reset() to reload the Flashdisk on windows')
#   machine.reset()

except Exception:
  pyb_led_red.on()
  raise
