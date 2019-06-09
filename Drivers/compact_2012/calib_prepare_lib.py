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

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

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
    for cutoff_frequency in np.logspace(0, 2, 30, endpoint=True) *0.001:
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

if __name__ == '__main__':
        # random signal for testing
        np.random.seed(0)
        signallength = 1000
        stepsize_V = np.random.randn(signallength) * 5e-6 + 19e-6

        stepsum_dac_12, stepsize_dac_12, correction_dac_12 = find_solution(stepsize_V)

        plt.plot(correction_dac_12)
        plt.plot(stepsum_dac_12)
        plt.plot(stepsum_dac_12+correction_dac_12)
        plt.plot(np.ones_like(stepsize_dac_12) * dac_12_limit_h_dac_12)
        plt.plot(np.ones_like(stepsize_dac_12) * dac_12_mid_dac_12)
        plt.plot(np.ones_like(stepsize_dac_12) * dac_12_limit_l_dc_12)
        plt.show()
