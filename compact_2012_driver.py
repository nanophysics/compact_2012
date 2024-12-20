
import os
import math
import time
import pathlib
import logging

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

logger = logging.getLogger('compact_2012')

logger.setLevel(logging.DEBUG)

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).absolute().parent
try:
    import mp
    import mp.version
    import mp.micropythonshell
    import mp.pyboard_query
except ModuleNotFoundError as ex:
    raise Exception('The module "mpfshell2" is missing. Did you call "pip -r requirements.txt"?')

REQUIRED_MPFSHELL_VERSION='100.9.13'
if mp.version.FULL < REQUIRED_MPFSHELL_VERSION:
    raise Exception(f'Your "mpfshell" has version "{mp.version.FULL}" but should be higher than "{REQUIRED_MPFSHELL_VERSION}". Call "pip install --upgrade mpfshell2"!')

import compact_2012_dac
import calib_prepare_lib
import config_all
from src_micropython.micropython_portable import *

HWTYPE_COMPACT_2012 = 'compact_2012'

# ranges and scaling
DICT_GAIN_2_VALUE = {
    '+/- 10 V, change by hand': 1.0,
    '+/- 5 V, change by hand': 0.5,
    '+/- 2 V, change by hand': 0.2,
    '+/- 1 V, change by hand': 0.1,
    '+/- 0.5 V, change by hand': 0.05,
    '+/- 0.2 V, change by hand': 0.02,
    '+/- 0.1 V, change by hand': 0.01,
}
CHANGE_BY_HAND = ', change by hand'

# datasheet RTC-10hz, 395ohm, at 1000 Ohm RL 19.7 V/(m/s)
GEOPHONE_VOLTAGE_TO_PARTICLEVELOCITY_FACTOR=19.7
# gainINA103 = 1000, dividerR49R51 = 0.33,  VrefMCP3201 = 3.3 therefore VrefMCP3201/gainINA103/dividerR49R51 = 0.01
F_GEOPHONE_VOLTAGE_FACTOR=0.01/4096.0
GEOPHONE_MAX_AGE_S=1.0

SAVE_VALUES_TO_DISK_TIME_S=5.0

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
        # This is 'False' till we get our correct value from Labber.
        self.b_initialized = False
        self.index = index
        self.f_value_V:float = 0.0
        self.f_gain = 1.0

    def get_gain_string(self):
        for str_gain, f_gain in DICT_GAIN_2_VALUE.items():
            if math.isclose(f_gain, self.f_gain):
                return str_gain.replace(CHANGE_BY_HAND, '')
        return '??? {:5.1f}'.format(self.f_gain)

class Compact2012:
    def __init__(self, board=None, hwserial=''):
        if board is not None:
            assert hwserial == ''
            self.board = board
        else:
            assert board is None
            hwserial = hwserial.strip()
            if hwserial == '':
                hwserial = None
            self.board = mp.pyboard_query.ConnectHwtypeSerial(product=mp.pyboard_query.Product.Pyboard, hwtype=HWTYPE_COMPACT_2012, hwserial=hwserial)
        assert isinstance(self.board, mp.pyboard_query.Board)
        self.board.systemexit_hwtype_required(hwtype=HWTYPE_COMPACT_2012)
        self.board.systemexit_firmware_required(min='1.14.0', max='1.14.0')
        self.compact_2012_serial = self.board.identification.HWSERIAL
        try:
            self.compact_2012_config = config_all.dict_compact2012[self.compact_2012_serial]
        except KeyError:
            self.compact_2012_config = config_all.dict_compact2012[config_all.SERIAL_UNDEFINED]
            print()
            print(f'WARNING: The connected "compact_2012" has serial "{self.compact_2012_serial}". However, this serial in unknown!')
            serials_defined = sorted(config_all.dict_compact2012.keys())
            serials_defined.remove(config_all.SERIAL_UNDEFINED)
            print(f'INFO: "config_all.py" lists these serials: {",".join(serials_defined)}')

        print(f'INFO: {HWTYPE_COMPACT_2012} connected: {self.compact_2012_config}')

        self.__calibrationLookup = None
        self.ignore_str_dac12 = False
        self.f_write_file_time_s = 0.0
        self.filename_values = DIRECTORY_OF_THIS_FILE / f'Values-{self.compact_2012_serial}.txt'
        self.list_dacs = [Dac(i) for i in range(DACS_COUNT)]

        self.obj_time_span_set_dac = TimeSpan(100, 'set_dac()')
        self.obj_time_span_get_status = TimeSpan(100, 'get_status()')

        # The time when the dac was set last.
        self.f_last_dac_set_s = 0.0

        # if the driver is not working anymore
        self.b_pyboard_error = False
        self.i_pyboard_geophone_dac = 0
        self.f_pyboard_geophone_read_s = 0

        self.shell = self.board.mpfshell
        self.fe = self.shell.MpFileExplorer
        # Download the source code
        self.shell.sync_folder(DIRECTORY_OF_THIS_FILE / 'src_micropython', FILES_TO_SKIP=['config_identification.py'])
        # Start the program
        self.fe.exec_('import micropython_logic')
        self.sync_status_get()
        self.load_calibration_lookup()

    def close(self):
        self.save_values_to_file(b_force=True)
        self.fe.close()

    def load_calibration_lookup(self):
        if self.compact_2012_serial is None:
            return
        calib_correction_data = calib_prepare_lib.CalibCorrectionData(self.compact_2012_serial)
        self.__calibrationLookup = calib_correction_data.load()

    def reset_calibration_lookup(self):
        self.__calibrationLookup = None

    def save_values_to_file(self, b_force=False):
        '''
            Save current values to disk
            Only save once per SAVE_VALUES_TO_DISK_TIME_S for better performance.
        '''
        if not b_force:
            if time.perf_counter() < self.f_write_file_time_s:
                return
        self.f_write_file_time_s = time.perf_counter() + SAVE_VALUES_TO_DISK_TIME_S

        with self.filename_values.open('w') as f:
            str_date_time = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())

            f.write('{}\n'.format(str_date_time))
            f.write('''compact_2012
While measuring with Labber, this file is written every {} seconds. If you delete this file, Labber will write it again.
When Labber crashes and the instrument server loses the values, you may manually copy and paste the values from this file to the instrument server config. Set cfg. Then start instrument server.
Voltages: physical values in volt; the voltage at the OUT output.\n
Details: https://github.com/nanophysics/compact_2012/blob/master/doc_installation/README_recovery_crash.md\n\n'''.format(SAVE_VALUES_TO_DISK_TIME_S))
            for obj_Dac in self.list_dacs:
                f.write('DA{} {:8.8f} V     (range, jumper, {})\n'.format(obj_Dac.index+1, obj_Dac.f_value_V*obj_Dac.f_gain, obj_Dac.get_gain_string()))

    def get_dac(self, index):
        '''
           Returns the current Voltage
        '''
        assert 0 <= index < DACS_COUNT
        obj_Dac = self.list_dacs[index]
        if obj_Dac.b_initialized:
            return obj_Dac.f_value_V
        return 0.0

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
            assert 0 <= index < DACS_COUNT
            obj_Dac = self.list_dacs[index]
            f_DA_OUT_desired_V = d['f_DA_OUT_desired_V']
            f_gain = d.get('f_gain', 1.0)
            f_DA_OUT_sweep_VperSecond = d.get('f_DA_OUT_sweep_VperSecond', 0.0)

            def get_actual_DA_OUT_V():
                if not obj_Dac.b_initialized:
                    # None: Labber just started.
                    # We assume that we where on this voltage before.
                    obj_Dac.b_initialized = True
                    obj_Dac.f_value_V = f_DA_OUT_desired_V/f_gain

                return obj_Dac.f_value_V*f_gain

            def set_new_DA_OUT_V(f_value_v):
                # Will set the value and update the dict
                obj_Dac.f_value_V = f_value_v/f_gain
                if obj_Dac.f_value_V > VALUE_PLUS_MIN_MAX_V:
                    obj_Dac.f_value_V = VALUE_PLUS_MIN_MAX_V
                if obj_Dac.f_value_V < -VALUE_PLUS_MIN_MAX_V:
                    obj_Dac.f_value_V = -VALUE_PLUS_MIN_MAX_V
                obj_Dac.f_gain = f_gain
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
        for obj_Dac in self.list_dacs:
            if not obj_Dac.b_initialized:
                print('INFO: Not all dac values initialized. ...Wait for labber to set all values...')
                return
        f_values_plus_min_v = [obj_Dac.f_value_V for obj_Dac in self.list_dacs]
        str_dac20, str_dac12 = compact_2012_dac.getDAC20DAC12HexStringFromValues(f_values_plus_min_v, calibrationLookup=self.__calibrationLookup)
        if self.ignore_str_dac12:
            str_dac12 = '0'*DACS_COUNT*DAC12_NIBBLES
        s_py_command = 'micropython_logic.set_dac("{}", "{}")'.format(str_dac20, str_dac12)
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
        str_status = self.fe.eval('micropython_logic.get_status()')
        self.obj_time_span_get_status.end()
        self.__update_status_return(str_status)

    def sync_set_user_led(self, on):
        assert isinstance(on, bool)
        self.fe.eval('micropython_logic.set_user_led({})'.format(on))

    def sync_set_geophone_led_threshold_percent_FS(self, threshold_percent_FS):
        assert isinstance(threshold_percent_FS, float)
        assert 0.0 <= threshold_percent_FS <= 100.0
        threshold_dac = threshold_percent_FS*4096.0//100.0
        assert 0.0 <= threshold_dac <= 4096
        self.fe.eval('micropython_logic.set_geophone_threshold_dac({})'.format(threshold_dac))

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

    #
    # Logic for 'calib_' only
    #
    def sync_calib_raw_init(self):
        '''
        Initializes the AD20
        '''
        self.fe.eval('micropython_logic.calib_raw_init()')

    def sync_calib_read_ADC24(self, iDac_index):
        strADC24 = self.fe.eval('micropython_logic.calib_read_ADC24({})'.format(iDac_index))
        iADC24 = int(strADC24)

        fADC24 = convert_ADC24_signed_to_V(iADC24)
        return iADC24, fADC24

    def sync_calib_raw_measure(self, filename, iDac_index, iDacStart, iDacEnd):
        '''
        Initializes the AD20
        '''
        assert iDacStart >= 0
        assert iDacEnd < DAC20_MAX
        assert iDacStart < iDacEnd
        assert 0 <= iDac_index < DACS_COUNT
        self.fe.eval('micropython_logic.calib_raw_measure("{}", {}, {}, {})'.format(filename, iDac_index, iDacStart, iDacEnd))
        pass

    def calib_raw_readfile(self, filename):
        filenameFull = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.fe.get(filename, filenameFull)

