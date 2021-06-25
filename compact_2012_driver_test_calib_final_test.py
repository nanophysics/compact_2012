import time
import compact_2012_driver

if __name__ == '__main__':
    driver = compact_2012_driver.Compact2012('COM10')
    driver.sync_set_geophone_led_threshold_percent_FS(10.0)
    driver.sync_calib_raw_init()

    iDacFix_index = 0
    iDacDUT_index = 1
    fDacMiddle = 0.0
    fDacPeak = 6e-4
    fDacIncrement = 1e-4

    print('fDacMiddle, fDac, fADC24, iADC24')

    fDac = fDacMiddle-fDacPeak
    while fDac < fDacMiddle+fDacPeak:
        # Measure
        dict_requested_values = {
            iDacFix_index: {
                'f_DA_OUT_desired_V': fDacMiddle,
                'f_gain': 1.0,
            },
            iDacDUT_index: {
                'f_DA_OUT_desired_V': fDac,
                'f_gain': 1.0,
            }
        }
        b_done, dict_changed_values = driver.sync_dac_set_all(dict_requested_values)

        # Wait to settle
        time.sleep(0.03)

        # Read from ADC
        iADC24, fADC24 = driver.sync_calib_read_ADC24()

        print(f'{fDacMiddle:12.9f}, {fDac:12.9f}, {fADC24:12.9f}, {iADC24:8d}')

        fDac += fDacIncrement

    driver.close()
