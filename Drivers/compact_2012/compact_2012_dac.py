'''

'''

from micropython_portable import *

def continuity_lookup(dac28_value):
    '''
      Allow future extension: Lookup table for continuity

      The DAC8 will have a gain for 2 digits of the DAC20.
      This will allow to use DAC8 to drive a continuity offset.
      This method will:
      Take the last significant 8 bits and device it by 2.
    '''
    dac28_value_lookup = dac28_value
    last_8_bits = dac28_value % 0x100
    dac28_value_lookup -= last_8_bits
    last_8_bits = last_8_bits//2
    dac28_value_lookup += last_8_bits
    assert dac28_value - dac28_value_lookup < 0x100
    return dac28_value_lookup

def getDAC28FromValue(value_plus_min_v):
    # scale to [0..DAC28_MAX-1]
    dac28_value = DAC28_MAX*(value_plus_min_v+VALUE_PLUS_MIN_MAX_V)/VALUE_PLUS_MIN_MAX_V/2.0
    dac28_value = int(dac28_value)
    # clip to [0..DAC28_MAX-1]
    dac28_value_clipped = min(max(dac28_value, 0), DAC28_MAX-1)
    # Allow future extension: Lookup table for continuity
    dac28_value_lookup = continuity_lookup(dac28_value_clipped)
    return dac28_value_lookup

def getDAC28HexStringFromValue(value_plus_min_v):
    '''
        Convert the desired voltage into a integer from [0..DAC28_MAX-1].

        >>> getDAC28HexStringFromValue(-10.0)
        '0000000'
        >>> getDAC28HexStringFromValue(0.0)
        '8000000'
        >>> getDAC28HexStringFromValue(18.0e-6)
        '8000078'
        >>> getDAC28HexStringFromValue(5.0)
        'C000000'
        >>> getDAC28HexStringFromValue(10.0)
        'FFFFF7F'
        >>> getDAC28HexStringFromValue(15.0)
        'FFFFF7F'
    '''
    dac28_value = getDAC28FromValue(value_plus_min_v)
    return DAC28_FORMAT_HEX.format(dac28_value)

def getDAC28HexStringFromValues(f_values_plus_min_v):
    '''
        Convert the desired voltage into a integer from [0..DAC28_MAX-1].

        >>> str_dac28 = getDAC28HexStringFromValues((-10.0, -5.0, -2.0, -1.0, 0.0, 1.0, 2.0, 5.0, 10.0, 15.0))
        >>> str_dac28
        '000000040000006666633733331980000008CCCC66999994CC000000FFFFF7FFFFFF7F'
        >>> assert len(str_dac28) == DACS_COUNT*DAC28_NIBBLES
        >>> clear_dac_nibbles()
        >>> set_dac_nibbles(str_dac28)
        >>> dac20_nibbles
        bytearray(b'1FFFFF1FFFFF1C000019999918CCCC180000173333166666140000100000')
        >>> dac8_nibbles
        bytearray(b'07F03307F03300003304C033066033000033019033033033000033000033')

        >>> dac8_bytes_value1to9, dac8_bytes_value10 = splice_dac8()
        >>> len(dac8_bytes_value1to9)
        27
        >>> len(dac8_bytes_value10)
        3
        >>> binascii.hexlify(dac8_bytes_value1to9)
        b'07f03307f03300003304c033066033000033019033033033000033'
        >>> binascii.hexlify(dac8_bytes_value10)
        b'000033'
    '''
    assert len(f_values_plus_min_v) == DACS_COUNT

    str_dac28 = ''.join(map(getDAC28HexStringFromValue, f_values_plus_min_v))

    return str_dac28

if __name__ == '__main__':
    import doctest
    doctest.testmod()

