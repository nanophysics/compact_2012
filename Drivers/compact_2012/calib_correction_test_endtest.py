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

bFast = False

# Drivers\compact_2012\calibration_correction\20190606_01\calibration_correction.txt
# dac=0: argmin=774144 (4.765625000 V)
# dac=0: argmax=688128 (3.125000000 V)
# dac=1: argmin=790528 (5.078125000 V)
# dac=1: argmax=343275 (-3.452548981 V)
list_measurements = (
    (0, 4.765625000),
    (0, 3.125000000),
    (1, 5.078125000),
    (1, -3.452548981),
)

# Drivers\compact_2012\calibration_correction\20190606_02\calibration_correction.txt
# dac=0: argmin=774144 (4.765625000 V)
# dac=0: argmax=688128 (3.125000000 V)
# dac=1: argmin=790528 (5.078125000 V)
# dac=1: argmax=567424 (0.822753906 V)
# dac=2: argmin=790528 (5.078125000 V)
# dac=2: argmax=688128 (3.125000000 V)
# dac=3: argmin=788480 (5.039062500 V)
# dac=3: argmax=352384 (-3.278808594 V)
# dac=4: argmin=544768 (0.390625000 V)
# dac=4: argmax=557056 (0.625000000 V)
# dac=5: argmin=544768 (0.390625000 V)
# dac=5: argmax=557056 (0.625000000 V)
# dac=6: argmin=544768 (0.390625000 V)
# dac=6: argmax=510080 (-0.270996094 V)
# dac=7: argmin=544768 (0.390625000 V)
# dac=7: argmax=557056 (0.625000000 V)
# dac=8: argmin=544768 (0.390625000 V)
# dac=8: argmax=495744 (-0.544433594 V)
# dac=9: argmin=544768 (0.390625000 V)
# dac=9: argmax=522368 (-0.036621094 V)
list_measurements = (
    (0, 4.765625000),
    (0, 3.125000000),
    (1, 5.078125000),
    (1, 0.822753906),
    (2, 5.078125000),
    (2, 3.125000000),
    (3, 5.039062500),
    (3, -3.278808594),
    (4, 0.390625000),
    (4, 0.625000000),
    (5, 0.390625000),
    (5, 0.625000000),
    (6, 0.390625000),
    (6, -0.270996094),
    (7, 0.390625000),
    (7, 0.625000000),
    (8, 0.390625000),
    (8, -0.544433594),
    (9, 0.390625000),
    (9, -0.036621094),
)

list_measurements = (
    (0, 3.125000000),
    (1, 0.822753906),
    (3, 5.078125000),
    (6, -0.270996094),
    (9, -0.036621094),
)

def getOtherDAC(iDac_index0):
    assert 0 <= iDac_index0 < 10
    dictDacFix = {}
    DAC_COUNT = 10
    for i in range(0, DAC_COUNT, 2):
        dictDacFix[i] = i+1
        dictDacFix[i+1] = i
    return dictDacFix[iDac_index0]

if __name__ == '__main__':
    driver = compact_2012_driver.Compact2012()
    driver.sync_set_geophone_led_threshold_percent_FS(10.0)
    driver.sync_calib_raw_init()

    fDacPeak_V = 70e-6
    fDacIncrement_V = 0.5e-6
    if bFast:
        fDacPeak_V = 25e-6
        fDacIncrement_V = 1.0e-6

    for iDacDUT_index0, fDacMiddle_V in list_measurements:
        iDacFix_index0 = getOtherDAC(iDacDUT_index0)

        filename = f'calibration_correction/{driver.compact_2012_serial}/calib_correction_test_endtest_out_DA{iDacDUT_index0+1:02d}_{fDacMiddle_V:10.9f}.txt'
        print(filename)

        with open(filename, 'w') as f:
            for indent, do_lookup, use_str_dac in (
                    (0, True, True),
                    (4, False, True),
                    (8, False, False),
                ):
                driver.ignore_str_dac12 = not use_str_dac
                if do_lookup:
                    driver.load_calibration_lookup()
                else:
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

                f.write('\t'*indent)
                f.write('\t'.join(('fADC24_V', 'fDac_set_V', 'fDac_get_V', 'fDac_get_error_V')))
                f.write('\n')
                f.flush()

                fDac_set_V = fDacMiddle_V-fDacPeak_V
                while fDac_set_V < fDacMiddle_V+fDacPeak_V:
                    # Measure
                    print('.', end='')
                    dict_requested_values = {
                        iDacFix_index0: {
                            'f_DA_OUT_desired_V': fDacMiddle_V,
                            'f_gain': 1.0,
                        },
                        iDacDUT_index0: {
                            'f_DA_OUT_desired_V': fDac_set_V,
                            'f_gain': 1.0,
                        }
                    }
                    b_done, dict_changed_values = driver.sync_dac_set_all(dict_requested_values)

                    # Wait to settle
                    if bFast:
                      time.sleep(0.01)
                    else:
                      time.sleep(0.03)

                    # Read from ADC
                    fADC24_V = 0.0
                    MEASUREMENTS = 10
                    if bFast:
                        MEASUREMENTS = 1
                    for i in range(MEASUREMENTS):
                        _iADC24, _fADC24_V = driver.sync_calib_read_ADC24(iDacDUT_index0)
                        fADC24_V += _fADC24_V

                    fADC24_V /= MEASUREMENTS
                    fDac_error_V = fDac_set_V-fDacMiddle_V
                    if iDacFix_index0%2 == 0:
                        # iDacFix_index0=0,2,4
                        fDac_error_V -= fADC24_V
                        fDac_get_V = fDacMiddle_V+fADC24_V
                    else:
                        # iDacFix_index0=1,3,5
                        fDac_error_V += fADC24_V
                        fDac_get_V = fDacMiddle_V-fADC24_V

                    f.write('\t'*indent)
                    f.write(f'{fADC24_V:12.9f}\t{fDac_set_V:12.9f}\t{fDac_get_V:12.9f}\t{fDac_error_V:12.9f}')
                    f.write('\n')
                    f.flush()

                    fDac_set_V += fDacIncrement_V

                f.write(f'\n')
                f.flush()
                print()

    driver.close()
