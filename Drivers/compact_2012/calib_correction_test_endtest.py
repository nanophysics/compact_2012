#
# This file uses the 30bit DAC using the calibration_lookup.
# To see if the calibration_lookup works fine, a error of the DAC20 is needed.
# In 'Drivers\compact_2012\calibration_correction\20190606_01\calibration_correction.txt' is a list of the biggests errors ov every DAC20.
# Use this script to sweep over such an error.
#
# Add such an error in 'fDacMiddle_V' below.
# Start this script.
# Copy 'Drivers/compact_2012/calib_correction_test_endtest_out.txt' into TODO OpenOffice Calc.
#

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

    iDacFix_index0 = 1
    iDacDUT_index0 = 0
    fDacMiddle_V = 5.703105927
    fDacPeak_V = 70e-6
    fDacIncrement_V = 0.5e-6

    filename = f'Drivers/compact_2012/calibration_correction/{driver.compact_2012_serial}/calib_correction_test_endtest_out_DA{iDacFix_index0+1:02d}_{fDacMiddle_V:10.9f}.txt'
    print(filename)

    with open(filename, 'w') as f:
        for do_lookup, use_str_dac in (
                (True, True),
                (False, True),
                (False, False),
            ):
            driver.ignore_str_dac12 = not use_str_dac
            if not do_lookup:
                driver.reset_calibration_lookup()

            print(f'do_lookup={do_lookup} use_str_dac={use_str_dac} ', end='')

            f.write(f'compact_2012_serial={driver.compact_2012_serial}\n')
            f.write(f'do_lookup={do_lookup}\n')
            f.write(f'use_str_dac={use_str_dac}\n')
            f.write(f'iDacFix_index0={iDacFix_index0} (DA{iDacFix_index0+1})\n')
            f.write(f'iDacDUT_index0={iDacDUT_index0} (DA{iDacDUT_index0+1})\n')
            f.write(f'fDacMiddle_V={fDacMiddle_V}\n')
            f.write(f'fDacPeak_V={fDacPeak_V}\n')
            f.write(f'fDacIncrement_V={fDacIncrement_V}\n')

            f.write('fADC24_V, fDac_V, fDac_error_V\n')

            fDac_V = fDacMiddle_V-fDacPeak_V
            while fDac_V < fDacMiddle_V+fDacPeak_V:
                # Measure
                print('.', end='')
                dict_requested_values = {
                    iDacFix_index0: {
                        'f_DA_OUT_desired_V': fDacMiddle_V,
                        'f_gain': 1.0,
                    },
                    iDacDUT_index0: {
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
                if iDacFix_index0%2 == 0:
                    fDac_error_V += fADC24_V
                else:
                    fDac_error_V -= fADC24_V

                f.write(f'{fADC24_V:12.9f}, {fDac_V:12.9f}, {fDac_error_V:12.9f}\n')

                fDac_V += fDacIncrement_V

            f.write(f'\n')
            f.flush()
            print()

    driver.close()
