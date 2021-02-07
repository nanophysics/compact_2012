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
    driver = compact_2012_driver.Compact2012()
    driver.sync_set_geophone_led_threshold_percent_FS(5.0)

    if True:
        while(True):
            Spannung = float(input("Spannung -10 bis 10 V? "))
            set({
                    0: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                    1: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                    2: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                    3: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                    4: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                    5: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                    6: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                    7: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                    8: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                    9: {
                      'f_DA_OUT_desired_V': Spannung,
                      'f_gain': 1.0,
                    },
                })
