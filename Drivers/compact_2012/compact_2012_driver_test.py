import time
import compact_2012_driver

if __name__ != '__main__':
    driver = compact_2012_driver.Compact2012('COM7')
    driver.sync_set_geophone_led_threshold_percent_FS(10.0)

    if False:
        while True:
            driver.sync_status_get()
            driver.debug_geophone_print()
            time.sleep(0.4)

    if False:
        start = time.time()
        COUNT = 100
        for i in range(COUNT):
              driver.sync_dac_set_all({0: {'f_DA_OUT_desired_V': -2.5,}})
              driver.sync_dac_set_all({0: {'f_DA_OUT_desired_V': 2.5,}})
        print('Average time for {}: {}ms'.format(COUNT, (time.time()-start)/COUNT/2.0*1000.0))

    for f_DA_OUT_desired_V in (-2.0, 0.0, 2.0):
        driver.sync_dac_set_all({
            0: {'f_DA_OUT_desired_V': f_DA_OUT_desired_V, 'f_gain': 0.5, },
            1: {'f_DA_OUT_desired_V': -f_DA_OUT_desired_V, 'f_gain': 0.5, },
        })
        pass

    def set(dict_requested_values):
        while True:
            b_done, dict_changed_values = driver.sync_dac_set_all(dict_requested_values)
            print('dict_changed_values: {}'.format(dict_changed_values))
            print('geophone_percent_FS:                                    {:3.1f}%'.format(driver.get_geophone_percent_FS()))
            if b_done:
                print('done')
                break

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
