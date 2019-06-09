#
# Compact_2012
#
# Measure the DAC's of Compact_2012 and store
# the result in 'calib_raw_'-files.
#


import uos
import utime
print('This is "main.py". uos.getcwd()="{}"'.format(uos.getcwd()))

for filename in ('config_serial.py', 'micropython_ads1219.py', 'micropython_portable.py', 'micropython_logic.py'):
  print('execfile("{}")'.format(filename))
  execfile(filename)


try:
  timer_blink.callback(None)

  calib_raw_init()

  # 650h: Total
  # 50h: Pro DAC
  # 3h: Pro File (16 File for every DAC)
  iDacFileSize = DAC20_MAX//16
  # Show progress every 10%
  iDacProgress = iDacFileSize//10
  # iDacFileSize = 100

  list_files = uos.listdir()

  for iDacA_index in range(0, DACS_COUNT, 2):
    for iDacStart in range(0, DAC20_MAX, iDacFileSize):
      # iDacA_index = 0
      # iDacStart=0x80000
      # iDacEnd=0x80000+100
      # iDacEnd=0xFFFFF
      filename = 'calib_raw_{}_dac{}-{}.txt'.format(SERIAL, iDacA_index, iDacStart//iDacFileSize)
      if filename in list_files:
        print('{} exists. Skipped'.format(filename))
        continue

      FILENAME_TMP = 'tmp.txt'

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
          iTotalMeasurementsRemaining = DAC20_MAX*(DACS_COUNT-iDacA_index)//2 + DAC20_MAX-iDac
          fTimeTotalRemaining_ms = iTotalMeasurementsRemaining * fTimePerMeasurement_ms
          print('{}: {:0.0f}% {:0.1f}h remaining for this file. {:0.1f}h remaining total.'.format(
              filename, 
              100.0*fPercentRemaining,
              fTimeRemaining_ms/1000.0/60.0/60.0,
              fTimeTotalRemaining_ms/1000.0/60.0/60.0
          ))

      time_start_ms = utime.ticks_ms()
      iDacEnd = iDacStart+iDacFileSize
      calib_raw_measure(FILENAME_TMP, SERIAL, iDacA_index, iDacStart, iDacEnd, f_status=status)
      uos.rename(FILENAME_TMP, filename)
      print('{}: {}%'.format(filename, 100))

  p_LED_GREEN_out.on()
  print('DONE: success!')

# except KeyboardInterrupt:
#   pyb_led_red.on()
#   print('KeyboardInterrupt! machine.reset() to reload the Flashdisk on windows')
#   machine.reset()

except Exception:
  pyb_led_red.on()
  raise
