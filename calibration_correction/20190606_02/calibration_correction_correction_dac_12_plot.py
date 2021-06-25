#import io
#import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

numpy_file = np.load('calibration_correction.npz')

data = numpy_file['data']
shape = data.shape
channel = 0
correction_dac_12 = data[channel]
length = correction_dac_12.size

for channel in range(shape[0]):
    plt.plot(data[channel])
    #print(channel)

#print (length)
plt.plot(np.ones_like(correction_dac_12) * 2**12)
plt.plot(np.ones_like(correction_dac_12) * 0.0)

plt.show()
