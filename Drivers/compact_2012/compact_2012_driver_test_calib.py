import time
import compact_2012_driver

if __name__ == '__main__':
    driver = compact_2012_driver.Compact2012('COM10')
    driver.sync_set_geophone_led_threshold_percent_FS(10.0)

    driver.sync_calib_raw_init()

    iDacA_index = 0
    filename = 'calib_raw_dac{}_2019-06-08.txt'.format(iDacA_index)
    driver.sync_calib_raw_measure(filename, iDacA_index=iDacA_index, iDacStart=0x00000, iDacEnd=0x00010)
    driver.calib_raw_readfile(filename)
    driver.close()
