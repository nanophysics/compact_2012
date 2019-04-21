
import os
import sys
import re
import math
import time
import binascii
import platform

str_32bit = platform.architecture()[0]
if str_32bit != '32bit':
    raise Exception('Only 32 platform is supported due to a limitation in "pyserial". In Labber set "Run in 32-bit mode"!')

directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(directory, 'compact2012_mpfshell'))
sys.path.insert(0, os.path.join(directory, 'compact2012_pyserial'))
from mp.mpfexp import MpFileExplorer, RemoteIOError

import compact2012_dac
from micropython_portable import *

'''
    Naming conventions
        PEP8
        https://realpython.com/python-pep8/
        Start of variable: datatype
            b_xx      Boolean
            str_xx    String
            f_xx      Float
            i_xx      Integer
            dict_xx   Dictionary
            list_xx   List or Tuple
        End of variable: unit
            xx_V
            xx_m2
            xx_1
            xx_percent100

    Separation of logic
        pyboard
            every 100ms: polls for the geophone
            every 100ms: initializes DAC20. But only if no traffic detected
            flashes the red geophone led if movement detected
            flashed the blue communication led if traffic detected
            keeps track of status:
                pyboard_status
                    b_error: if the driver is not working anymore
                    i_geophone_dac
                    i_geophone_age_ms
                This status may be retreived from the pyboard using get_status()
            update of DAC20/DAC8:
                set_dac():
                    sets both DAC20 and DAC8
                    pyboard_status
        pc-driver
            cache all 10 f_dac_v
            cache all 10 i_dac_set_time_ms
            cache pyboard_status

'''

# datasheet RTC-10hz, 395ohm, at 1000 Ohm RL 19.7 V/(m/s)
GEOPHONE_VOLTAGE_TO_PARTICLEVELOCITY_FACTOR=19.7
# gainINA103 = 1000, dividerR49R51 = 0.33,  VrefMCP3201 = 3.3 therefore VrefMCP3201/gainINA103/dividerR49R51 = 0.01
F_GEOPHONE_VOLTAGE_FACTOR=0.01/4096.0
GEOPHONE_MAX_AGE_S=1.0
LED_VIBRATION_THRESHOLD_100PERCENT_V=0.001

SAVE_VALUES_TO_DISK_TIME_S=1.0

# sweep set interval, in seconds
F_SWEEPINTERVAL_S = 0.03

class Dac:
    def __init__(self, index):
        self.index = index
        self.f_value_V = 0.0


class Compact2012:
    def __init__(self, str_port):
        if re.match(r'^COM\d+$', str_port) is None:
            raise Exception('Expected a string like "COM5", but got "{}"'.format(str_port))
        str_port2 = 'ser:' + str_port

        self.list_dacs = list(map(lambda i: Dac(i), range(DACS_COUNT)))

        # The time when the dac was set last.
        self.f_last_dac_set_s = 0.0

        # if the driver is not working anymore
        self.b_pyboard_error = False
        self.i_pyboard_geophone_dac = 0
        self.f_pyboard_geophone_read_s = 0

        self.fe = MpFileExplorer(str_port2, reset=True)
        self.__sync_init()
    
    def __sync_init(self):
        for filename in ('micropython_portable.py', 'micropython_logic.py'):
            filenameFull = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            # self.fe.put(filenameFull, filename)
            self.fe.execfile(filenameFull)
        self.sync_status_get()

    def __time_since_last_dac_set_s(self):
        return time.monotonic() - self.f_last_dac_set_s

    def close(self):
        self.fe.close()

    def get_dac(self, index):
        '''
           Returns the current Voltage
        '''
        assert 0 <= index < DACS_COUNT
        return self.list_dacs[index].f_value_V

    def __calculate_and_set_new_dac(self, dict_requested_values):
        '''
            Will set the new dac-values:
            self.list_dacs[index].f_value_V = ...
            returns b_done, b_need_wait_before_DAC_set
        '''
        b_done = True
        b_need_wait_before_DAC_set = False
        dict_changed_values = {}

        for index, d in dict_requested_values.items():
            assert 0 <= index <= DACS_COUNT
            obj_Dac = self.list_dacs[index]
            f_dac_desired_V = d['f_dac_desired_V']
            f_sweep_VperSecond = d.get('f_sweep_VperSecond', 0.0)

            def set_value(f_value_v):
                # Will set the value and update the dict
                obj_Dac.f_value_V = f_value_v
                dict_changed_values[index] = f_value_v

            if math.isclose(0.0, f_sweep_VperSecond):
                # No sweeping
                set_value(f_dac_desired_V)
                continue

            # Sweeping requested
            assert f_sweep_VperSecond >= 0.0
            f_desired_step_V = f_dac_desired_V - obj_Dac.f_value_V
            if math.isclose(0.0, f_desired_step_V):
                # We are on the requested voltage. Nothing to do
                continue

            # We need to sweep
            b_need_wait_before_DAC_set = True
            f_possible_step = F_SWEEPINTERVAL_S*f_sweep_VperSecond
            if abs(f_desired_step_V) < f_possible_step:
                # We can set the final voltage
                set_value(f_dac_desired_V)
                continue

            # The sweep rate is limiting
            b_done = False
            f_step_V = math.copysign(f_possible_step, f_desired_step_V)
            set_value(obj_Dac.f_value_V + f_step_V)

        return b_done, b_need_wait_before_DAC_set, dict_changed_values

    def sync_dac_set_all(self, dict_requested_values):
        '''
            dict_requested_values = {
                0: # Optional. The DAC [0..9]
                    {
                        'f_dac_desired_V': 5.5, # The value to set
                        'f_sweep_VperSecond': 0.1, # Optional
                    }
            }

            return: b_done, {
                0: 5.1, # Actual value
            }

            This method will receive try to set the values of the dacs.
            If the call is following very shortly after the last call, it may delay before setting the DACs.
            If required, f_sweep_VperSecond will be used for small voltage increments.
            The effective set values will be returned. To be used for updateing the display and the log output.
            If b_done == False, the labber driver muss call this method again with the same parameters.
        '''
        b_done, b_need_wait_before_DAC_set, dict_changed_values = self.__calculate_and_set_new_dac(dict_requested_values)

        if b_need_wait_before_DAC_set:
            # We have to make sure, that the last call was not closer than F_SWEEPINTERVAL_S
            time_to_sleep_s = F_SWEEPINTERVAL_S - self.__time_since_last_dac_set_s()
            if time_to_sleep_s > 0.005:
                assert time_to_sleep_s <= F_SWEEPINTERVAL_S
                time.sleep(time_to_sleep_s)
        
        # Now set the new values to the DACs
        self.__sync_dac_set()

        return b_done, dict_changed_values

    def __sync_dac_set(self):
        '''
            Send to new dac values to the pyboard.
            Return pyboard_status.
        '''
        f_values_plus_min_v = list(map(lambda obj_Dac: obj_Dac.f_value_V, self.list_dacs))
        str_dac28 = compact2012_dac.getDAC28HexStringFromValues(f_values_plus_min_v)
        s_py_command = 'set_dac("{}")'.format(str_dac28)
        pyboard_status = self.fe.eval(s_py_command)
        return pyboard_status

    def sync_status_get(self):
        '''
            Poll for the pyboard_status
        '''
        str_status = self.fe.eval('get_status()')
        list_pyboard_status = eval(str_status)
        assert len(list_pyboard_status) == 3
        self.b_pyboard_error = list_pyboard_status[0]
        self.i_pyboard_geophone_dac = list_pyboard_status[1]
        self.f_pyboard_geophone_read_s = time.time() - list_pyboard_status[2]/1000.0

    def sync_set_user_led(self, on):
        assert isinstance(on, bool)
        self.fe.eval('set_user_led({})'.format(on))

    def sync_set_geophone_led_threshold_percent(self, threshold_percent):
        assert isinstance(threshold_percent, float)
        assert 0.0 <= threshold_percent <= 100.0
        threshold_dac = threshold_percent/F_GEOPHONE_VOLTAGE_FACTOR*LED_VIBRATION_THRESHOLD_100PERCENT_V/100.0
        assert 0.0 <= threshold_dac <= 4096
        self.fe.eval('set_geophone_threshold_dac({})'.format(threshold_dac))


        # self.led_red_vibration_on = self.geophone_voltage/LED_VIBRATION_THRESHOLD_100PERCENT_V  > self.led_vibration_threshold_percent/100.0
        # self.led_red_vibration_on = self.i_pyboard_geophone_dac*F_GEOPHONE_VOLTAGE_FACTOR/LED_VIBRATION_THRESHOLD_100PERCENT_V  > self.led_vibration_threshold_percent/100.0
        # # Convert
        # self.led_red_vibration_on = self.i_pyboard_geophone_dac > self.led_vibration_threshold_percent/F_GEOPHONE_VOLTAGE_FACTOR*LED_VIBRATION_THRESHOLD_100PERCENT_V/100.0

    def x(self):
        return self.__read_geophone_voltage()

    def __sync_get_geophone(self):
        f_geophone_age_s = time.time() - self.f_pyboard_geophone_read_s
        if f_geophone_age_s > GEOPHONE_MAX_AGE_S:
            # This will read 'self.i_pyboard_geophone_dac'
            self.sync_status_get()

    def __read_geophone_voltage(self):
        self.__sync_get_geophone()
        return self.i_pyboard_geophone_dac * F_GEOPHONE_VOLTAGE_FACTOR

    def get_geophone_percent(self):
        f_percent = self.__read_geophone_voltage()/LED_VIBRATION_THRESHOLD_100PERCENT_V*100.0
        return max(0.0, min(100.0, f_percent))

    def get_geophone_particle_velocity(self):
        return self.__read_geophone_voltage()/GEOPHONE_VOLTAGE_TO_PARTICLEVELOCITY_FACTOR

