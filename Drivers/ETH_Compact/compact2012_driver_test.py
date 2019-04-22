import time
import compact2012_driver

def set(dict_requested_values):
    while True:
        b_done, dict_changed_values = driver.sync_dac_set_all(dict_requested_values)
        print('dict_changed_values: {}'.format(dict_changed_values))
        print('geophone_percent_FS:                                    {:3f} mV'.format(1000.0*driver.get_geophone_percent_FS()))
        if b_done:
            print('done')
            break

if __name__ == '__main__':
    driver = compact2012_driver.Compact2012('COM7')
    driver.sync_set_geophone_led_threshold_percent_FS(10.0)

    if False:
        while True:
            driver.sync_status_get()
            driver.debug_geophone_print()
            time.sleep(0.4)

    set({
        0: {
          'f_dac_desired_V': 2.5,
          'f_sweep_VperSecond': 5.0,
        },
        1: {
          'f_dac_desired_V': 1.5,
          'f_sweep_VperSecond': 5.0,
        },
        2: {
          'f_dac_desired_V': 5.0,
        },
    })

    set({
        0: {
          'f_dac_desired_V': 2.0,
          'f_sweep_VperSecond': 1.0,
        },
        2: {
          'f_dac_desired_V': 10.0,
        },
    })
    
    driver.close()
