import time
import compact_2012_driver

if __name__ == '__main__':
    driver = compact_2012_driver.Compact2012('COM10')
    driver.sync_set_geophone_led_threshold_percent_FS(10.0)

    driver.sync_calib_raw_init()

    iDacA_index = 0
    iDacStart=0x80000
    iDacEnd=0x80000+1000
    iDacEnd=0xFFFFF
    COUNT = iDacEnd-iDacStart
    filename = 'calib_raw_dac{}_2019-06-08.txt'.format(iDacA_index)
    start = time.time()
    driver.sync_calib_raw_measure(filename, iDacA_index=iDacA_index, iDacStart=iDacStart, iDacEnd=iDacEnd)
    time_avg_measurement_s = (time.time()-start)/COUNT/2.0
    time_total_s = 2**20 * 10 * time_avg_measurement_s
    print('Average time for {}: {}ms. Total {}d'.format(COUNT, time_avg_measurement_s*1000.0, time_total_s/3600.0/24.0))
    driver.calib_raw_readfile(filename)
    driver.close()
