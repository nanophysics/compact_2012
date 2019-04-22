import time
import compact_2012_driver

def set(dict_requested_values):
    while True:
        b_done, dict_changed_values = driver.sync_dac_set_all(dict_requested_values)
        print('dict_changed_values: {}'.format(dict_changed_values))
        print('geophone_percent_FS:                                    {:3.1f}%'.format(driver.get_geophone_percent_FS()))
        if b_done:
            print('done')
            break

if __name__ == '__main__':
    driver = compact_2012_driver.Compact2012('COM7')
    driver.sync_set_geophone_led_threshold_percent_FS(10.0)

    if True:
        while True:
            driver.sync_status_get()
            driver.debug_geophone_print()
            time.sleep(0.4)

    set({
        0: {
          'f_DA_OUT_desired_V': 2.5,
          'f_DA_OUT_sweep_VperSecond': 5.0,
        },
        1: {
          'f_DA_OUT_desired_V': 1.5,
          'f_DA_OUT_sweep_VperSecond': 5.0,
          'f_gain': 0.5,
        },
        2: {
          'f_DA_OUT_desired_V': 5.0,
          'f_gain': 0.2,
        },
    })

    set({
        0: {
          'f_DA_OUT_desired_V': 2.0,
          'f_DA_OUT_sweep_VperSecond': 1.0,
        },
        2: {
          'f_DA_OUT_desired_V': 10.0,
          'f_gain': 0.2,
        },
    })
    
    driver.close()
