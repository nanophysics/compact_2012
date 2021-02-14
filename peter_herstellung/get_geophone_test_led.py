'''
Set the output voltage.
It assumes the the jumpers are set to +/- 10V
--help

--com=10
DA1=0.1 DA2=0.1

'''
import re
import os
import sys
import pathlib
import argparse
import time

DIRECTORY_OF_THIS_FILE=pathlib.Path(__file__).parent
os.chdir(DIRECTORY_OF_THIS_FILE.parent.joinpath('Drivers/compact_2012'))
sys.path.insert(0, '.')
import compact_2012_driver

reDA = re.compile(r'^DA(?P<channel>\d+)=(?P<voltage>[\d\.-]+)$')
CHANNEL_COUNT=10

DESCRIPTION=f'''Set the output voltage.
It assumes the the jumpers are set to +/- 10V.
Example {__file__} --COM=5 DA1=1.1 DA2=3.5
'''
def parse_arguments():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--com', dest='comport', type=str,
                                            help='The com port. If not provided, try to find one.')
    parser.add_argument('voltages', metavar='DAx=1.0', type=str, nargs='*',
                                            help='The output voltages. If not provided: 0 V. 1<=DAx<=10')

    args = parser.parse_args()

    def exit():
        print()
        parser.print_help()
        sys.exit()

    if args.comport is not None:
        try:
            int(args.comport)
        except:
            print(f'ERROR: Expected a integer but got "{args.comport}"!')
            exit()

    dictVoltages = {}
    for arg_string in args.voltages:
        match = reDA.match(arg_string)
        if match is None:
            print(f'ERROR: Unexpected parameter "{arg_string}"!')
            exit()
        voltage_string = match.group('voltage')
        try:
            voltage_V = float(voltage_string)
        except:
            print(f'ERROR: Unexpected voltage "{voltage_string}" in "{arg_string}"!')
            exit()
        channel_string = match.group('channel')
        try:
            channel1 = int(channel_string)
        except:
            print(f'ERROR: Unexpected channel "{channel_string}" in "{arg_string}"!')
            exit()
        if not (1 <= channel1 <= CHANNEL_COUNT):
            print(f'ERROR: Channel "{channel1}" out of range in "{arg_string}"!')
            exit()
        dictVoltages[channel1-1] = {'f_DA_OUT_desired_V': voltage_V, 'f_gain': 1.0 }

    return args.comport, dictVoltages


def main():
    comport, dictVoltages = parse_arguments()

    if comport is not None:
        comport = f'COM{comport}'

    # These is the essential access to compact_2020
    # Connect
    driver = compact_2012_driver.Compact2012(comport)
    # Use dictionary to set 'f_DA_OUT_desired_V' and 'f_gain'
    driver.sync_dac_set_all(dictVoltages)

    while True:
        driver.sync_status_get()
        driver.debug_geophone_print()
        driver.sync_set_geophone_led_threshold_percent_FS(10.0)
        time.sleep(0.4)

    driver.close()
    


if __name__ == '__main__':
    main()
