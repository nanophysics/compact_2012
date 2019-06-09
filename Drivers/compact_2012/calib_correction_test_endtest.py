import time
import compact_2012_driver

if __name__ == '__main__':
    driver = compact_2012_driver.Compact2012('COM10')
    driver.sync_set_geophone_led_threshold_percent_FS(10.0)
    driver.sync_calib_raw_init()

    # dac=0: argmin=610303 (1.640605927 V)
    # dac=0: argmax=577533 (1.015567780 V)
    # dac=1: argmin=610303 (1.640605927 V)
    # dac=1: argmax=577534 (1.015586853 V)

    iDacFix_index = 1
    iDacDUT_index = 0
    fDacMiddle_V = 1.640605927
    fDacPeak_V = 2e-4
    fDacIncrement_V = 1e-6

    with open(f'Drivers/compact_2012/calib_correction_test_endtest_out.txt', 'w') as f:
        for do_lookup, ignore_str_dac12 in (
                (True, False),
                (True, True),
                (False, True),
            ):
            driver.ignore_str_dac12 = ignore_str_dac12
            if ignore_str_dac12:
                driver.reset_calibration_lookup()

            print('do_lookup={do_lookup} ignore_str_dac12={ignore_str_dac12} ', end='')

            f.write(f'do_lookup={do_lookup}\n')
            f.write(f'ignore_str_dac12={ignore_str_dac12}\n')
            f.write(f'iDacFix_index={iDacFix_index}\n')
            f.write(f'iDacDUT_index={iDacDUT_index}\n')
            f.write(f'fDacMiddle_V={fDacMiddle_V}\n')
            f.write(f'fDacPeak_V={fDacPeak_V}\n')
            f.write(f'fDacIncrement_V={fDacIncrement_V}\n')

            f.write('fADC24_V, fDac_V, fDac_error_V\n')

            fDac_V = fDacMiddle_V-fDacPeak_V
            while fDac_V < fDacMiddle_V+fDacPeak_V:
                # Measure
                print('.', end='')
                dict_requested_values = {
                    iDacFix_index: {
                        'f_DA_OUT_desired_V': fDacMiddle_V,
                        'f_gain': 1.0,
                    },
                    iDacDUT_index: {
                        'f_DA_OUT_desired_V': fDac_V,
                        'f_gain': 1.0,
                    }
                }
                b_done, dict_changed_values = driver.sync_dac_set_all(dict_requested_values)

                # Wait to settle
                time.sleep(0.03)

                # Read from ADC
                fADC24_V = 0.0
                MEASUREMENTS=10
                for i in range(MEASUREMENTS):
                    _iADC24, _fADC24_V = driver.sync_calib_read_ADC24()
                    fADC24_V += _fADC24_V

                fADC24_V /= MEASUREMENTS
                fDac_error_V = fDac_V-fDacMiddle_V
                if iDacFix_index%2 == 0:
                    fDac_error_V += fADC24_V
                else:
                    fDac_error_V -= fADC24_V

                f.write(f'{fADC24_V:12.9f}, {fDac_V:12.9f}, {fDac_error_V:12.9f}\n')

                fDac_V += fDacIncrement_V

            f.write(f'\n')
            f.flush()
            print()

    driver.close()
