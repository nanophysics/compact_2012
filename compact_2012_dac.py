'''

'''
import itertools
from src_micropython.micropython_portable import *

# constants of the schematic of compact_2012_da
dac_12_ref_V    = 3.3
dac_12_bit = 12
R232 = 1.00E+06
R233 = 2.00E+04
step_teiler_1_V = dac_12_ref_V / (R232 + R233) * R233
R234 = 9.10E+05
R235 = 1.00E+06
R236 = 1.00E+06
ad5791_imp = 3400.0
step_teiler_2_V = step_teiler_1_V / (R234+R235+R236) * ad5791_imp

# falls keine Kalibrationsmessung vorhanden,theoretischer sollwert:
f_fallback_dac_12_int_per_V = 2**12 / step_teiler_2_V

def getValueFromDAC20(dac20_value):
    '''Assert gain=1.0'''
    '''DAC20 -> Float(V)'''
    assert isinstance(dac20_value, int)
    assert 0 <= dac20_value < DAC20_MAX
    value = VALUE_PLUS_MIN_MAX_V * 2.0 * dac20_value / DAC20_MAX - VALUE_PLUS_MIN_MAX_V
    return value

def getDAC20FromValue(value_plus_min_v):
    '''Float(V) -> DAC20'''
    assert isinstance(value_plus_min_v, float)

    # scale to [0..DAC20_MAX-1]
    dac20_value = DAC20_MAX*(value_plus_min_v+VALUE_PLUS_MIN_MAX_V)/VALUE_PLUS_MIN_MAX_V/2.0
    dac20_value = int(dac20_value)
    # clip to [0..DAC20_MAX-1]
    dac20_value_clipped = min(max(dac20_value, 0), DAC20_MAX-1)

    assert isinstance(dac20_value_clipped, int)
    return dac20_value_clipped

def getDAC20DAC12IntFromValue(value_plus_min_v, calibrationLookup=None, iDac_index=0):
    '''
        Convert the desired voltage into a integer from [0..DAC30_MAX-1].

        >>> list(map('0x{:05X}'.format, getDAC20DAC12IntFromValue(-10.0)))
        ['0x00000', '0x00000']
        >>> list(map('0x{:05X}'.format, getDAC20DAC12IntFromValue(0.0)))
        ['0x80000', '0x00000']
        >>> list(map('0x{:05X}'.format, getDAC20DAC12IntFromValue(18.0e-6)))
        ['0x80000', '0x003CF']
        >>> list(map('0x{:05X}'.format, getDAC20DAC12IntFromValue(19.0e-6)))
        ['0x80000', '0x00405']
        >>> list(map('0x{:05X}'.format, getDAC20DAC12IntFromValue(20.0e-6)))
        ['0x80001', '0x00032']
        >>> list(map('0x{:05X}'.format, getDAC20DAC12IntFromValue(5.0)))
        ['0xC0000', '0x00000']
        >>> list(map('0x{:05X}'.format, getDAC20DAC12IntFromValue(10.0)))
        ['0xFFFFF', '0x00409']
        >>> list(map('0x{:05X}'.format, getDAC20DAC12IntFromValue(15.0)))
        ['0xFFFFF', '0x00409']
    '''
    assert 0 <= iDac_index <= DACS_COUNT

    if value_plus_min_v > VALUE_PLUS_MIN_MAX_V:
        value_plus_min_v = VALUE_PLUS_MIN_MAX_V
    if value_plus_min_v < -VALUE_PLUS_MIN_MAX_V:
        value_plus_min_v = -VALUE_PLUS_MIN_MAX_V

    dac20_value = getDAC20FromValue(value_plus_min_v)

    if calibrationLookup is not None:
        # calibrationLookup(): This function returns a DAC12 offset for every 'dac20_value'.
        f_dac_12_int_per_V, dac12_correction = calibrationLookup(iDac_index, dac20_value)
        assert dac12_correction < DAC12_MAX_CORRECTION_VALUE
    else:
        dac12_correction = 0
        f_dac_12_int_per_V = f_fallback_dac_12_int_per_V

    f_dac12_v = value_plus_min_v - getValueFromDAC20(dac20_value)
    dac12_value = f_dac12_v * f_dac_12_int_per_V + dac12_correction
    dac12_value = int(dac12_value)
    if dac12_value < 0:
        print('WARNING - strange calibration data! Expected "dac12_value>=0" but got {}'.format(dac12_value))
        dac12_value = 0
    if dac12_value >= DAC12_MAX:
        print('WARNING - strange calibration data! Expected "dac12_value<DAC12_MAX" but got {}'.format(dac12_value))
        dac12_value = DAC12_MAX-1

    return dac20_value, dac12_value

def getDAC20DAC12HexStringFromValues(f_values_plus_min_v, calibrationLookup=None):
    '''
        Convert the desired voltage into a integer from [0..DAC30_MAX-1].

        >>> str_dac20, str_dac12 = getDAC20DAC12HexStringFromValues((-10.0, -5.0, -2.0, -1.0, 0.0, 1.0, 2.0, 5.0, 9.0, 15.0))
        >>> str_dac20
        '00000400006666673333800008CCCC99999C0000F3333FFFFF'
        >>> str_dac12
        '00000019D0CE00033A26C0000CE409'
        >>> assert len(str_dac20) == DACS_COUNT*DAC20_NIBBLES
        >>> assert len(str_dac12) == DACS_COUNT*DAC12_NIBBLES
        >>> clear_dac_nibbles()
        >>> set_dac20_nibbles(str_dac20)
        >>> dac20_nibbles
        bytearray(b'1FFFFF1F33331C000019999918CCCC180000173333166666140000100000')
        >>> set_dac12_nibbles(str_dac12)
        >>> dac12_nibbles
        bytearray(b'04093300CE33000033026C33033A3300003300CE33019D33000033000033')

        >>> dac12_bytes_value1to9, dac12_bytes_value10 = splice_dac12(dac12_nibbles)
        >>> len(dac12_bytes_value1to9)
        27
        >>> len(dac12_bytes_value10)
        3
        >>> binascii.hexlify(dac12_bytes_value1to9)
        b'04093300ce33000033026c33033a3300003300ce33019d33000033'
        >>> binascii.hexlify(dac12_bytes_value10)
        b'000033'
    '''
    assert len(f_values_plus_min_v) == DACS_COUNT

    list_i_dac20  = []
    list_i_dac12 = []
    for iDac_index, f_value_plus_min_v in zip(itertools.count(), f_values_plus_min_v):
        dac20_value, dac12_value = getDAC20DAC12IntFromValue(f_value_plus_min_v, calibrationLookup, iDac_index)
        assert isinstance(dac12_value, int)
        assert isinstance(dac20_value, int)
        list_i_dac20.append(dac20_value)
        list_i_dac12.append(dac12_value)

    assert len(list_i_dac20) == DACS_COUNT
    assert len(list_i_dac12) == DACS_COUNT

    str_dac20 = getHexStringFromListInt20(list_i_dac20)
    str_dac12 = getHexStringFromListInt12(list_i_dac12)

    assert len(str_dac20) == DACS_COUNT * DAC20_NIBBLES
    assert len(str_dac12) == DACS_COUNT * DAC12_NIBBLES

    return str_dac20, str_dac12

if __name__ == '__main__':
    import doctest
    doctest.testmod()

