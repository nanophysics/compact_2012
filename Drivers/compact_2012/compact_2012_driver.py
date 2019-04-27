
import os
import sys
import re
import math
import time
import logging

logger = logging.getLogger('compact_2012')

logger.setLevel(logging.DEBUG)

directory = os.path.dirname(os.path.abspath(__file__))
for subproject in ('compact_2012_mpfshell', 'compact_2012_pyserial'):
    filename_requirements = os.path.join(directory, subproject, 'requirements.txt')
    if not os.path.exists(filename_requirements):
        raise Exception('The file "{}" is missing. You have git-clone the subproject "{}" too!'.format(filename_requirements, subproject))
    sys.path.insert(0, os.path.join(directory, subproject))

from mp.mpfexp import MpFileExplorer, RemoteIOError

import compact_2012_dac
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
            every x ms: polls for the geophone
            every x ms: initializes DAC20. But only if no traffic detected
            flashes the red geophone led if movement detected
            flashed the blue communication led if traffic detected
            keeps track of status:
                pyboard_status
                    b_error: if the driver is not working anymore
                    i_geophone_dac
                    i_geophone_age_ms
                This status may be retreived from the pyboard using get_status()
            update of DAC20/DAC12:
                set_dac(str_dac20, str_dac12):
                    sets both DAC20 and DAC12
                    pyboard_status
        pc-driver
            cache all 10 f_dac_v
            cache f_last_dac_set_s (the time the DACs where set the last time)
            cache pyboard_status

'''

# datasheet RTC-10hz, 395ohm, at 1000 Ohm RL 19.7 V/(m/s)
GEOPHONE_VOLTAGE_TO_PARTICLEVELOCITY_FACTOR=19.7
# gainINA103 = 1000, dividerR49R51 = 0.33,  VrefMCP3201 = 3.3 therefore VrefMCP3201/gainINA103/dividerR49R51 = 0.01
F_GEOPHONE_VOLTAGE_FACTOR=0.01/4096.0
GEOPHONE_MAX_AGE_S=1.0

SAVE_VALUES_TO_DISK_TIME_S=1.0

# sweep set interval, in seconds
F_SWEEPINTERVAL_S = 0.03

class TimeSpan:
    '''
      A helper to measure the time required to communicate with the pyboard.
    '''
    def __init__(self, i_measurements, s_name):
        self._i_measurements = i_measurements
        self._s_name = s_name
        self._reset()
    
    def _reset(self):
        self._f_time_start_s = None
        self._i_count = 0
        self._f_sum_ms = 0.0
        self._f_min_ms = 10000000.0
        self._f_max_ms = 0.0
    
    def start(self):
        self._f_time_start_s = time.perf_counter()
    
    def end(self):
        if self._i_count >= self._i_measurements:
            logger.debug('{}: min={:4.1f}ms avg={:4.1f}ms max={:4.1f}ms'.format(
                self._s_name,
                self._f_min_ms,
                self._f_sum_ms/self._i_count,
                self._f_max_ms
            ))
            self._reset()
            return
        assert self._f_time_start_s is not None
        f_time_elapsed_ms = 1000.0*(time.perf_counter() - self._f_time_start_s)
        self._i_count += 1
        self._f_sum_ms += f_time_elapsed_ms
        self._f_min_ms = min(self._f_min_ms, f_time_elapsed_ms)
        self._f_max_ms = max(self._f_max_ms, f_time_elapsed_ms)

class Dac:
    def __init__(self, index):
        self.index = index
        self.f_value_V = 0.0

class Compact2012:
    def __init__(self, str_port):
        if re.match(r'^COM\d+$', str_port) is None:
            raise Exception('Expected a string like "COM5", but got "{}"'.format(str_port))
        str_port2 = 'ser:' + str_port

        self.f_write_file_time_s = 0.0
        self.str_filename_values = os.path.join(directory, 'Values-{}.txt'.format(str_port))
        self.list_dacs = list(map(lambda i: Dac(i), range(DACS_COUNT)))

        self.obj_time_span_set_dac = TimeSpan(100, 'set_dac()')
        self.obj_time_span_get_status = TimeSpan(100, 'get_status()')

        # The time when the dac was set last.
        self.f_last_dac_set_s = 0.0

        # if the driver is not working anymore
        self.b_pyboard_error = False
        self.i_pyboard_geophone_dac = 0
        self.f_pyboard_geophone_read_s = 0

        self.fe = MpFileExplorer(str_port2, reset=True)
        self.__sync_init()
        # Is this still needed?
        # self.load_values_from_file()

    def close(self):
        self.save_values_to_file()
        self.fe.close()

    def load_values_from_file(self):
        '''
            Load ADC-Values from disk
        '''
        if not os.path.exists(self.str_filename_values):
            print('"{}": No Compact settings found. Initialize to 0.'.format(self.str_filename_values))
            # keep track of values (10 voltages)
            return

        # open and convert to numbers
        with open(self.str_filename_values, 'r') as f:
            s = f.read()
        
        str_error = '"{}": Compact settings expected 10 integer values got "{}". Initialize to 0.'.format(self.str_filename_values, s)
        # s: 8.936,4.0,3.56,0.0,0.0,0.0,0.0,0.0,0.0,0.0
        list_values = s.split(',')
        if len(list_values) != DACS_COUNT:
            print(str_error)
            return
        try:
            list_values = map(float, list_values)
        except ValueError:
            print(str_error)
            return
        for i, f_value_V in enumerate(list_values):
            self.list_dacs[i].f_value_V = f_value_V

    def save_values_to_file(self, b_force=False):
        '''
            Save current values to disk
            Only save once per SAVE_VALUES_TO_DISK_TIME_S for better performance.
        '''
        if not b_force:
            if time.perf_counter() < self.f_write_file_time_s:
                return
        self.f_write_file_time_s = time.perf_counter() + SAVE_VALUES_TO_DISK_TIME_S
        def f(obj_Dac):
            return '{:0.4f}'.format(obj_Dac.f_value_V)
        list_values = map(f, self.list_dacs)
        s = ','.join(list_values)
        with open(self.str_filename_values, 'w') as f:
            f.write(s)

    def __sync_init(self):
        for filename in ('micropython_portable.py', 'micropython_logic.py'):
            filenameFull = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            # self.fe.put(filenameFull, filename)
            self.fe.execfile(filenameFull)
        self.sync_status_get()

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
            f_DA_OUT_desired_V = d['f_DA_OUT_desired_V']
            f_gain = d.get('f_gain', 1.0)
            f_DA_OUT_sweep_VperSecond = d.get('f_DA_OUT_sweep_VperSecond', 0.0)

            def get_actual_DA_OUT_V():
                return obj_Dac.f_value_V*f_gain

            def set_new_DA_OUT_V(f_value_v):
                # Will set the value and update the dict
                obj_Dac.f_value_V = f_value_v/f_gain
                dict_changed_values[index] = f_value_v

            if math.isclose(0.0, f_DA_OUT_sweep_VperSecond):
                # No sweeping
                if not math.isclose(f_DA_OUT_desired_V, get_actual_DA_OUT_V()):
                    set_new_DA_OUT_V(f_DA_OUT_desired_V)
                continue

            # Sweeping requested
            assert f_DA_OUT_sweep_VperSecond >= 0.0
            f_desired_step_V = f_DA_OUT_desired_V - get_actual_DA_OUT_V()
            if math.isclose(0.0, f_desired_step_V):
                # We are on the requested voltage. Nothing to do
                continue

            # We need to sweep
            b_need_wait_before_DAC_set = True
            f_possible_step = F_SWEEPINTERVAL_S*f_DA_OUT_sweep_VperSecond
            if abs(f_desired_step_V) < f_possible_step:
                # We can set the final voltage
                set_new_DA_OUT_V(f_DA_OUT_desired_V)
                continue

            # The sweep rate is limiting
            b_done = False
            f_step_V = math.copysign(f_possible_step, f_desired_step_V)
            set_new_DA_OUT_V(get_actual_DA_OUT_V() + f_step_V)

        return b_done, b_need_wait_before_DAC_set, dict_changed_values

    def sync_dac_set_all(self, dict_requested_values):
        '''
            dict_requested_values = {
                0: # Optional. The DAC [0..9]
                    {
                        'f_DA_OUT_desired_V': 5.5, # The value to set
                        'f_DA_OUT_sweep_VperSecond': 0.1, # Optional
                        'f_gain': 0.5, # Optional. f_DA_OUT_desired_V=f_dac_desired_V*f_gain
                    }
            }

            return: b_done, {
                0: 5.1, # Actual value DA_OUT
            }

            This method will receive try to set the values of the dacs.
            If the call is following very shortly after the last call, it may delay before setting the DACs.
            If required, f_DA_OUT_sweep_VperSecond will be used for small voltage increments.
            The effective set values will be returned. To be used for updateing the display and the log output.
            If b_done == False, the labber driver muss call this method again with the same parameters.
        '''
        b_done, b_need_wait_before_DAC_set, dict_changed_values = self.__calculate_and_set_new_dac(dict_requested_values)

        if b_need_wait_before_DAC_set:
            # We have to make sure, that the last call was not closer than F_SWEEPINTERVAL_S
            OVERHEAD_TIME_SLEEP_S = 0.001
            time_to_sleep_s = F_SWEEPINTERVAL_S - (time.perf_counter() - self.f_last_dac_set_s) - OVERHEAD_TIME_SLEEP_S
            if time_to_sleep_s > 0.001: # It doesn't make sense for the operarting system to stop for less than 1ms
                assert time_to_sleep_s <= F_SWEEPINTERVAL_S
                time.sleep(time_to_sleep_s)

        # Now set the new values to the DACs
        self.f_last_dac_set_s = time.perf_counter()
        self.__sync_dac_set()

        return b_done, dict_changed_values

    def __sync_dac_set(self):
        '''
            Send to new dac values to the pyboard.
            Return pyboard_status.
        '''
        f_values_plus_min_v = list(map(lambda obj_Dac: obj_Dac.f_value_V, self.list_dacs))
        str_dac20, str_dac12 = compact_2012_dac.getDAC20DAC12HexStringFromValues(f_values_plus_min_v)
        s_py_command = 'set_dac("{}", "{}")'.format(str_dac20, str_dac12)
        self.obj_time_span_set_dac.start()
        
        str_status = self.fe.eval(s_py_command)

        self.obj_time_span_set_dac.end()
        self.__update_status_return(str_status)
        self.save_values_to_file()


    def __update_status_return(self, str_status):
        list_pyboard_status = eval(str_status)
        assert len(list_pyboard_status) == 2
        self.b_pyboard_error = list_pyboard_status[0]
        self.i_pyboard_geophone_dac = list_pyboard_status[1]
        self.f_pyboard_geophone_read_s = time.perf_counter()

    def sync_status_get(self):
        '''
            Poll for the pyboard_status
        '''
        self.obj_time_span_get_status.start()
        str_status = self.fe.eval('get_status()')
        self.obj_time_span_get_status.end()
        self.__update_status_return(str_status)

    def sync_set_user_led(self, on):
        assert isinstance(on, bool)
        self.fe.eval('set_user_led({})'.format(on))

    def sync_set_geophone_led_threshold_percent_FS(self, threshold_percent_FS):
        assert isinstance(threshold_percent_FS, float)
        assert 0.0 <= threshold_percent_FS <= 100.0
        threshold_dac = threshold_percent_FS*4096.0//100.0
        assert 0.0 <= threshold_dac <= 4096
        self.fe.eval('set_geophone_threshold_dac({})'.format(threshold_dac))

    def debug_geophone_print(self):
        print('geophone:                      dac={:016b}={:04d} [0..4095], voltage={:06f}mV, percent={:04.01f}'.format(self.i_pyboard_geophone_dac, self.i_pyboard_geophone_dac, self.__read_geophone_voltage(), self.get_geophone_percent_FS()))

    def __sync_get_geophone(self):
        f_geophone_age_s = time.perf_counter() - self.f_pyboard_geophone_read_s
        if f_geophone_age_s > GEOPHONE_MAX_AGE_S:
            # This will read 'self.i_pyboard_geophone_dac'
            self.sync_status_get()

    def __read_geophone_voltage(self):
        self.__sync_get_geophone()
        return self.i_pyboard_geophone_dac*F_GEOPHONE_VOLTAGE_FACTOR

    def get_geophone_percent_FS(self):
        f_percent_FS = self.i_pyboard_geophone_dac/4096.0*100.0
        return f_percent_FS

    def get_geophone_particle_velocity(self):
        return self.__read_geophone_voltage()/GEOPHONE_VOLTAGE_TO_PARTICLEVELOCITY_FACTOR

