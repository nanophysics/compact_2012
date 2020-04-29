'''
Set the output voltage.
It assumes the the jumpers are set to +/- 10V
--help

--com=10
DA1=0.1 DA2=0.1

'''
import re
import sys
import pathlib
import argparse

DIRECTORY_OF_THIS_FILE=pathlib.Path(__file__).parent
sys.path.insert(0, str(DIRECTORY_OF_THIS_FILE / 'Drivers' / 'compact_2012'))
import compact_2012_driver

reDA = re.compile(r'DA(?P<channel>\d+)=(?P<voltage>[\d.]+)')
CHANNEL_COUNT=10

DESCRIPTION=f'''Set the output voltage.
It assumes the the jumpers are set to +/- 10V.
Example {__file__} --COM=5 DA1=1.1 DA2=3.5
'''
def parse_arguments():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--COM', dest='comport', type=str,
                                            help='The com port. If not provided, try to find one.')
    parser.add_argument('voltages', metavar='DAx=1.0', type=str, nargs='*',
                                            help='The output voltages. If not provided: 0 V')

    args = parser.parse_args()

    dictVoltages = {}
    for arg_string in args.voltages:
        match = reDA.match(arg_string)
        if match is None:
            print(f'ERROR: Unexpected parameter "{arg_string}"!')
            continue
        voltage_string = match.group('voltage')
        try:
            voltage_V = float(voltage_string)
        except:
            print(f'ERROR: Unexpected voltage "{voltage_string}" in "{arg_string}"!')
            continue
        channel_string = match.group('channel')
        try:
            channel0 = int(channel_string)
        except:
            print(f'ERROR: Unexpected channel "{channel_string}" in "{arg_string}"!')
            continue
        if not (0 < channel0 < CHANNEL_COUNT):
            print(f'ERROR: Channel "{channel0+1}" out of range in "{arg_string}"!')
        dictVoltages[channel0] = {'f_DA_OUT_desired_V': voltage_V, 'f_gain': 1.0 }

    for channel0 in range(CHANNEL_COUNT):
        voltage_V = 0.0
        try:
            voltage_V = dictVoltages[channel0]['f_DA_OUT_desired_V']
        except KeyError:
            pass
        print(f'  DA{channel0+1}={voltage_V} V')

    return args.comport, dictVoltages

def main():
    comport, dictVoltages = parse_arguments()

    driver = compact_2012_driver.Compact2012(f'COM{comport}')
    driver.sync_dac_set_all(dictVoltages)
    driver.close()

if __name__ == '__main__':
    main()
