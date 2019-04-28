'''
  This runs on Micropython and on the PC!
'''
import binascii

# DACS in compact2012
DACS_COUNT = 10
# Maximal output
VALUE_PLUS_MIN_MAX_V = 10.0

# AD5791 20 bit
# These are the registers of the 20 bit dac
DAC20_NIBBLES = 5
DAC20_BITS = DAC20_NIBBLES*4
DAC20_MAX = 2**DAC20_BITS
# '{:05X}' => '00000', '80000', 'A6666'
DAC20_FORMAT_HEX = '{:0' + str(DAC20_NIBBLES) + 'X}'

# AD5300  12 bit
# These are the registers of the 12 bit dac.
# The 12 bits are used as follows
# B11, B10: 0  These 2 bits may be used later using lookup-tables for linearity control
# B9 .. B0: x  These 10 bits are used to enhance the resolution of the last bit of the DAC20.
DAC12_NIBBLES = 3
DAC12_BITS = DAC12_NIBBLES*4
DAC12_MAX = 2**DAC12_BITS
# '{:03X}' => '000', '800', 'A66'
DAC12_FORMAT_HEX = '{:0' + str(DAC12_NIBBLES) + 'X}'

# DAC20 and 10 bits from DAC12
DAC30_MAX = 2**30

# The registers of the DAC20. These registers are described here:
#   https://www.analog.com/media/en/technical-documentation/data-sheets/ad5791.pdf "Table 10. DAC Register"
DAC20_REGISTER_BYTES = 3
DAC20_REGISTER_NIBBLES = 2*DAC20_REGISTER_BYTES

# This bitfield will be shifted through all 10 DAC20
dac20_nibbles = bytearray(DACS_COUNT*DAC20_REGISTER_NIBBLES)

# This bitfield will be shifted through all 10 DAC12
# A: The DAC12-shift-register will be sourced from the DAC20 shift-register.
# B: The last shift through the DAC12 is special.
#    Therefore 'dac12_bytes_value1to9' and 'dac12_bytes_value10'
dac12_nibbles = bytearray(DACS_COUNT*DAC20_REGISTER_NIBBLES)

def clear_dac_nibbles(init='3'):
    '''
        Initialize the shift-register
        Init with 3 to see what is not initialized.
    '''
    ord_init = ord(init)
    for i in range(len(dac20_nibbles)):
        dac12_nibbles[i] = dac20_nibbles[i] = ord_init

clear_dac_nibbles(init='3')

def set_dac20_nibbles(str_dac20):
    '''
       str_dac20: '00000400006666673333800008CCCC99999C0000FFFFFFFFFF'

       'str_dac20' is the HEX-string we get from the PC.
       We reassemble it to fit into the DAC20 shift registers.
       'binascii.unhexlify(dac20_nibbles)' will the be sent to DAC20.
    '''
    assert len(str_dac20) == DACS_COUNT*DAC20_NIBBLES

    # DAC20
    for i in range(DACS_COUNT):
        i_offset_in = (DACS_COUNT-1-i)*DAC20_NIBBLES
        i_offset_out = i*DAC20_REGISTER_NIBBLES

        dac20_nibbles[i_offset_out] = ord('1')
        for i in range(DAC20_NIBBLES):
            dac20_nibbles[i_offset_out+i+1] = ord(str_dac20[i_offset_in+i])

def set_dac12_nibbles(str_dac12):
    '''
       str_dac12: '0000002663330000CC1990003FF3FF'

       'str_dac12' is the HEX-string we get from the PC.
       We reassemble it to fit into the DAC20 shift registers.
       'binascii.unhexlify(dac12_nibbles)' will the be sent to DAC12.
    '''
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
