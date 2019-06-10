import itertools
import micropython_portable

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

    if False:
        filename = 'Drivers/compact_2012/calib_raw_dac0_2019-06-09a.txt'
        r = micropython_portable.CalibRawFileReader(filename)
        list_step_a_V, list_step_b_V = r.values()
        for iDac, step_a_V, step_b_V in zip(itertools.count(r.iDacStart), list_step_a_V, list_step_b_V):
            print('0x{:06X} {:12.9f} {:12.9f}'.format(iDac, step_a_V, step_b_V))
