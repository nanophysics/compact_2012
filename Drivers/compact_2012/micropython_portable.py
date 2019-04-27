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
# '{:05X}' => '00000', '80000', 'A6666'
DAC20_FORMAT_HEX = '{:0' + str(DAC20_NIBBLES) + 'X}'

# AD5300  12 bit
DAC12_NIBBLES = 3
DAC12_BITS = DAC12_NIBBLES*4
DAC12_MAX = 2**DAC12_BITS
# '{:03X}' => '000', '800', 'A66'
DAC12_FORMAT_HEX = '{:0' + str(DAC12_NIBBLES) + 'X}'

DAC30_MAX = 2**30

DAC20_REGISTER_BYTES = 3
DAC20_REGISTER_NIBBLES = 2*DAC20_REGISTER_BYTES
dac20_nibbles = bytearray(DACS_COUNT*DAC20_REGISTER_NIBBLES)
dac12_nibbles = bytearray(DACS_COUNT*DAC20_REGISTER_NIBBLES)

def clear_dac_nibbles(init='3'):
    for i in range(len(dac20_nibbles)):
        dac12_nibbles[i] = dac20_nibbles[i] = ord(init)

clear_dac_nibbles(init='3')

def set_dac20_nibbles(str_dac20):
    assert len(str_dac20) == DACS_COUNT*DAC20_NIBBLES

    # DAC20
    for i in range(DACS_COUNT):
        i_offset_in = (DACS_COUNT-1-i)*DAC20_NIBBLES
        i_offset_out = i*DAC20_REGISTER_NIBBLES

        # See https://www.analog.com/media/en/technical-documentation/data-sheets/ad5791.pdf "Table 10. DAC Register"
        dac20_nibbles[i_offset_out] = ord('1')
        for i in range(DAC20_NIBBLES):
            dac20_nibbles[i_offset_out+i+1] = ord(str_dac20[i_offset_in+i])

def set_dac12_nibbles(str_dac12):
    assert len(str_dac12) == DACS_COUNT*DAC12_NIBBLES

    # DAC12
    for i in range(DACS_COUNT):
        i_offset_in = (DACS_COUNT-1-i)*DAC12_NIBBLES
        i_offset_out = i*DAC20_REGISTER_NIBBLES

        # x=0, x=0, PD1=0, PD0=0, D11=0, D10=0, D9, D8
        # D7, D6, D5, D4, D3, D2, D1=0, D0=0
        dac12_nibbles[i_offset_out+0] = ord('0')
        for i in range(DAC12_NIBBLES):
            dac12_nibbles[i_offset_out+i+1] = ord(str_dac12[i_offset_in+i])


def splice_dac12(dac12_nibbles):
    dac12_bytes = binascii.unhexlify(dac12_nibbles)
    bytes_count = (DACS_COUNT-1)*DAC20_REGISTER_BYTES
    dac12_bytes_value1to9 = dac12_bytes[:bytes_count]
    dac12_bytes_value10 = dac12_bytes[bytes_count:]
    assert len(dac12_bytes_value1to9) == (DACS_COUNT-1)*DAC20_REGISTER_BYTES
    assert len(dac12_bytes_value10) == DAC20_REGISTER_BYTES
    return dac12_bytes_value1to9, dac12_bytes_value10
