'''
  This runs on Micropython and on the PC!
'''
import binascii

# DACS in compact2012
DACS_COUNT = 10
# Maximal output
VALUE_PLUS_MIN_MAX_V = 10.0

# AD5791	20 bit
DAC20_NIBBLES = 5
DAC20_BITS = DAC20_NIBBLES*4
DAC20_MAX = 2**DAC20_BITS

# AD5300  8 bit
DAC8_NIBBLES = 2
DAC8_BITS = DAC8_NIBBLES*4
DAC8_MAX = 2**DAC8_BITS

DAC28_NIBBLES = DAC8_NIBBLES+DAC20_NIBBLES
DAC28_BITS = DAC28_NIBBLES*4
DAC28_MAX = 2**DAC28_BITS
# '{:07X}' => '0000000', '8000000', 'A666666'
DAC28_FORMAT_HEX = '{:0' + str(DAC28_NIBBLES) + 'X}'

DAC20_REGISTER_BYTES = 3
DAC20_REGISTER_NIBBLES = 2*DAC20_REGISTER_BYTES
dac20_nibbles = bytearray(DACS_COUNT*DAC20_REGISTER_NIBBLES)
dac8_bytes = bytearray(DACS_COUNT*DAC20_REGISTER_BYTES)

def clear_dac_nibbles(char_init='3', i_init=3):
    for i in range(len(dac20_nibbles)):
        dac20_nibbles[i] = ord(char_init)

    for i in range(len(dac8_bytes)):
        dac8_bytes[i] = i_init

clear_dac_nibbles(char_init='3', i_init=3)

def set_dac_nibbles(str_dac28):
    assert len(str_dac28) == DACS_COUNT*DAC28_NIBBLES

    # DAC20
    for i in range(DACS_COUNT):
        i_offset_in = (DACS_COUNT-1-i)*DAC28_NIBBLES
        i_offset_out = i*DAC20_REGISTER_NIBBLES

        # See https://www.analog.com/media/en/technical-documentation/data-sheets/ad5791.pdf "Table 10. DAC Register"
        dac20_nibbles[i_offset_out] = ord('1')
        for i in range(DAC20_NIBBLES):
            dac20_nibbles[i_offset_out+i+1] = ord(str_dac28[i_offset_in+i])

    # DAC8
    for i in range(DACS_COUNT):
        i_offset_in = (DACS_COUNT-1-i)*DAC28_NIBBLES
        i_offset_out = i*DAC20_REGISTER_BYTES

        i_DAC8 = (int(str_dac28[i_offset_in+DAC20_NIBBLES+0], 16) << 4) + int(str_dac28[i_offset_in+DAC20_NIBBLES+1], 16)
        dac8_bytes[i_offset_out+0] = i_DAC8 >> 6           # x=0, x=0, PD1=0, PD0=0, D11=0, D10=0, D9, D8
        dac8_bytes[i_offset_out+1] = (i_DAC8 << 2) & 0xFF  # D7, D6, D5, D4, D3, D2, D1=0, D0=0

def splice_dac8():
    bytes_count = (DACS_COUNT-1)*DAC20_REGISTER_BYTES
    dac8_bytes_value1to9 = dac8_bytes[:bytes_count]
    dac8_bytes_value10 = dac8_bytes[bytes_count:]
    assert len(dac8_bytes_value10) == DAC20_REGISTER_BYTES
    return dac8_bytes_value1to9, dac8_bytes_value10
