import io
import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import micropython_portable
import compact_2012_dac

#
# Logic Peter to calculate 'calib_correction'.
#

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

# the correction value will be added to the 10 bit value later, terefore the allowed range is from 0 to 2**12-2**10
dac_12_limit_h_dac_12 =    2 ** dac_12_bit * 3 / 4
dac_12_mid_dac_12 = 2 ** dac_12_bit * 3 / 8
dac_12_limit_l_dc_12 = 0

def highpassfilter(inputarray, cutoff_frequency = 0.001):
    # Highpassfilter https://tomroelandts.com/articles/how-to-create-a-simple-high-pass-filter
    # https://fiiir.com/
    N = 231    # Filter length, must be odd. Value choosen experimentally.
    h = np.sinc(2 * cutoff_frequency * (np.arange(N) - (N - 1) / 2)) # Compute sinc filter.
    h *= np.blackman(N) # Apply window.
    h /= np.sum(h) # Normalize to get unity gain.
    h = -h    # Create a high-pass filter from the low-pass filter through spectral inversion.
    h[(N - 1) // 2] += 1
    inputarray_paded = np.pad(inputarray, (N, N), 'edge') # padding to reduce effects on the edge
    inputarray_paded_filtered = np.convolve(inputarray_paded, h , mode='same')
    inputarray_filtered = inputarray_paded_filtered[N:-N] #remove padding
    return inputarray_filtered

def find_solution(stepsize_V):
    stepsize_dac_12 = stepsize_V / step_teiler_2_V * 2 ** dac_12_bit
    stepsize_deviation_dac_12 = stepsize_dac_12 - np.median(stepsize_dac_12) # we only have to correct for the offset from the theoretical step value
    stepsum_dac_12 = np.cumsum(stepsize_deviation_dac_12)

    solution_found = False
    cutoff_frequency_found = 0.0
    for cutoff_frequency in np.logspace(-3, 2, 30, endpoint=True) *0.001:
        correction_dac_12 = np.around(-highpassfilter(stepsum_dac_12, cutoff_frequency)+dac_12_mid_dac_12).astype(int)
        correction_dac_12_cliped = np.clip(correction_dac_12, a_min = dac_12_limit_l_dc_12, a_max = dac_12_limit_h_dac_12)
        if (correction_dac_12 == correction_dac_12_cliped).all(): # ok, in usable range
            solution_found = True
            cutoff_frequency_found = cutoff_frequency
            break
        print('No solution found with {:f}'.format(cutoff_frequency))

    assert(solution_found)
    print('Solution found with {:f}'.format(cutoff_frequency_found))
    return stepsum_dac_12, stepsize_dac_12, correction_dac_12

def find_solution2(filename, calib_correction_data):
    r = micropython_portable.CalibRawFileReader(filename)
    list_step_a_V, list_step_b_V = r.values()

    stepsize_a_V = np.array(list_step_a_V)
    correction_dac_12 = find_solution3(stepsize_a_V)
    calib_correction_data.set_correction(iDacA_index=r.iDacA_index+0, data=correction_dac_12, iDacStart=r.iDacStart+1)

    stepsize_b_V = np.array(list_step_b_V)
    correction_dac_12 = find_solution3(stepsize_b_V)
    calib_correction_data.set_correction(iDacA_index=r.iDacA_index+1, data=correction_dac_12, iDacStart=r.iDacStart+1)


def find_solution3(stepsize_V):
    mean_V = stepsize_V.mean()
    assert 17e-6 < mean_V < 21e-6, 'Expected a step of about 19uV but got {} V. Check the cabeling!'.format(mean_V)
    stepsum_dac_12, stepsize_dac_12, correction_dac_12 = find_solution(stepsize_V)

    plt.plot(correction_dac_12)
    plt.plot(stepsum_dac_12)
    plt.plot(stepsum_dac_12+correction_dac_12)
    plt.plot(np.ones_like(stepsize_dac_12) * dac_12_limit_h_dac_12)
    plt.plot(np.ones_like(stepsize_dac_12) * dac_12_mid_dac_12)
    plt.plot(np.ones_like(stepsize_dac_12) * dac_12_limit_l_dc_12)
    plt.show()

    return correction_dac_12

#
# Classes to read and write 'calib_correction'
#
class CalibCorrectionData:
    def __init__(self):
        self.f_comments = io.StringIO()
        self.data = np.zeros(shape=[micropython_portable.DACS_COUNT, micropython_portable.DAC20_MAX], dtype=np.uint16, order='C')

    def set_correction(self, iDacA_index, data, iDacStart):
        '''
          'data' contains the calib_correction for 'dac_index'. The first dac-value in 'data' is 'iDacStart'
        '''
        assert 0 <= iDacA_index < micropython_portable.DACS_COUNT
        assert len(data.shape) == 1
        assert 0 <= data.shape[0] < micropython_portable.DAC20_MAX
        assert 0 <= iDacStart < micropython_portable.DAC20_MAX

        assert data.min >= 0
        assert data.max < micropython_portable.DAC12_MAX_CORRECTION_VALUE

        self.data[iDacA_index:iDacA_index+1, iDacStart:iDacStart+data.shape[0]] = data
        argmax = np.argmax(data)
        argmin = np.argmin(data)
        print(f'argmax={argmax}, argmin={argmin}\n')
        def print2(tag, offset):
            index = int(iDacStart+offset)
            value_v = compact_2012_dac.getValueFromDAC20(index)
            self.f_comments.write(f'dac={iDacA_index}: {tag}={index} ({value_v:0.9f} V)\n')
        print2('argmin', argmin)
        print2('argmax', argmax)
        # self.f_comments.write(f'dac={iDacA_index}: argmax={iDacStart+argmax} ({compact_2012_dac.getValueFromDAC20(iDacStart+argmax):0.9f} V), argmin={iDacStart+argmin} ({compact_2012_dac.getValueFromDAC20(iDacStart+argmin):0.9f} V)\n')

    def save(self, filename):
        np.savez_compressed(filename, data=self.data)
        # np.savez(filename, data=self.data)
        assert filename.endswith('.npz')
        filename_txt = filename.replace('.npz', '.txt')
        with open(filename_txt, 'w') as f:
            f.write(self.f_comments.getvalue())

    def load(self, filename):
        numpy_file = np.load(filename)
        self.data = numpy_file['data']
        assert self.data.shape == (micropython_portable.DACS_COUNT, micropython_portable.DAC20_MAX)

    def calibrationLookup(self, iDac_index, dac20_value):
        '''
            This function returns a DAC12 offset for every 'dac20_value'.
        '''
        assert 0 <= iDac_index < micropython_portable.DACS_COUNT
        assert 0 <= dac20_value < micropython_portable.DAC20_MAX

        dac12_value = self.data[iDac_index, dac20_value]
        dac12_value = int(dac12_value)
        return dac12_value


if __name__ == '__main__':
    if False:
        # random signal for testing
        np.random.seed(0)
        signallength = 1000
        stepsize_V = np.random.randn(signallength) * 5e-6 + 19e-6

        find_solution3(stepsize_V)

    if True:
        calib_correction_data = CalibCorrectionData()

        filename = 'Drivers/compact_2012/calib_raw_dac0_2019-06-09a.txt'
        find_solution2(filename, calib_correction_data)

        calib_correction_data.save('Drivers/compact_2012/calib_correction_a.npz')
