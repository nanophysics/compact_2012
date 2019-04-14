#!/usr/bin/env python

import Ni845x_Wrapper
import InstrumentDriver
import numpy as np
# import win32api
import time

class Error(Exception):
    pass

class Driver(InstrumentDriver.InstrumentWorker):
    """ This class implements the Acqiris card driver"""

    # ranges and scaling
    dRange = {'+/- 10 V, change by hand': 1.0,
              '+/- 5 V, change by hand': 0.5,
              '+/- 2 V, change by hand': 0.2,
              '+/- 1 V, change by hand': 0.1,
              '+/- 0.5 V, change by hand': 0.05,
              '+/- 0.2 V, change by hand': 0.02,
              '+/- 0.1 V, change by hand': 0.01}
    
    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # init object
        self.spi = None

        # open connection
        sAddress = str(self.comCfg.address)
        # USB0::0x3923::0x7514::01A39834::RAW
        self.spi = Ni845x_Wrapper.ETH_Compact(sAddress) 
    
        # Reset the usb connection (it must not change the applied voltages)
        self.log('ETH Compact Driver: Connection resetted at startup')
        self.spi.initialize()      

    def performClose(self, bError=False, options={}):
        """Perform the close instrument connection operation"""
        self.spi.closeConnection()


    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation. This function should
        return the actual value set by the instrument"""
        # keep track of multiple calls, to set multiple voltages efficiently
        if self.isFirstCall(options):
            self.dDacValuesToSet = {}
        if quant.name == 'Green LED':
            # set user LED
            self.spi.setUserLED(bool(value))            
        elif quant.name.endswith('-voltage'):
            # get index of channel to set
            # Hack...
            # Parse quant.name="DA3-voltage" -> 3 -> 2
            indx = int(quant.name.strip().split('-')[0][2:]) - 1
            # don't set, just add to dict with values to be set (value, rate)
            self.dDacValuesToSet[indx] = [value, sweepRate]
        elif quant.name.endswith('-jumper setting'):
            # get index of channel to set
            # Hack...
            # Parse quant.name="DA3-jumper" -> 3 -> 2
            indx = int(quant.name.strip().split('-')[0][2:]) - 1
            # read corresponding voltage to update scaling
            quant.setValue(value)
            self.readValueFromOther('DA%d-voltage' % (indx+1))
        # if final call and voltages have been changed, send them at once
        elif quant.name == 'Geophone red LED threshold':
            value = max(0.0, min(100.0, value))
            self.spi.led_vibration_threshold_percent = value
        if self.isFinalCall(options) and len(self.dDacValuesToSet)>0:
            self.setMultipleValues()
        return value


    def setMultipleValues(self):
        """Set multiple values at once, with support for sweeping"""
        # sweep set interval, in seconds
        dInterval_s = 0.03
        # create vectors of values to set for each channel
        dValues = {}
        dScale = {}
        for indx, [value, sweepRate] in self.dDacValuesToSet.items():
            # first, get and store scale for this channel
            sRange = self.getValue('DA%d-jumper setting' % (indx+1))
            dScale[indx] = self.dRange[sRange]
            # get old value from SPI, scale to actual voltage
            currValue = dScale[indx] * self.spi.getValue(indx)
            if sweepRate == 0.0 or value == currValue:
                # already at the final value or no sweeping, set single value
                dValues[indx] = np.array([value], dtype=float)
            else:
                # get number of steps
                dSweepTime = abs(value-currValue)/sweepRate
                nStep = int(np.ceil(dSweepTime/dInterval_s))
                # create step points, excluding start point
                dValues[indx] = np.linspace(currValue, value, nStep+1)[1:]
        # perform sweeping by setting values at each step
        nMaxStep = max([len(v) for v in dValues.values()])
        # 
        t0 = time.time()
        for n in range(nMaxStep):
            # set for all channels
            for indx, lValue in dValues.items():
                # check if more values to set for this channel
                if n < len(lValue):
                    # set new value, but do not send to instrument
                    self.spi.setValue(indx, lValue[n]/dScale[indx], send_to_instr=False)
                    # update the quantity to keep driver up-to-date
                    self.setValue('DA%d-voltage' % (indx+1),  lValue[n], 
                                  sweepRate=self.dDacValuesToSet[indx][1])
            # send the values to the DAC after all values have been updated
            self.spi.sendValues()
            # check if stopped 
            if self.isStopped():
                return
            # wait some time, if necessary (not for last step)
            if (n+1)<nMaxStep:
                dt = time.time() - t0
                waitTime = dInterval_s*(n+1) - dt
                if waitTime > 0.0:
                    self.wait(waitTime)


    def checkIfSweeping(self, quant):
        """Always return false, sweeping is done in loop"""
        return False

    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""
        # only implmeneted for geophone voltage
        if quant.name == 'Geophone percent':
            value = self.spi.readGeophonePercent()
        elif quant.name == 'Geophone particle velocity':
            value = self.spi.readGeophoneParticleVelocity()
        elif quant.name == 'Geophone red LED threshold':
            value = self.spi.led_vibration_threshold_percent
        elif quant.name.endswith('-voltage'):
            # get index of channel to get
            # Hack...
            # Parse quant.name="DA3-voltage" -> 3 -> 2
            indx = int(quant.name.strip().split('-')[0][2:]) - 1
            # get value from driver, then return scaled value
            sRange = self.getValue('DA%d-jumper setting' % (indx+1))
            scale = self.dRange[sRange]
            value = scale * self.spi.getValue(indx)
        else:
            # just return the quantity value
            value = quant.getValue()
        return value



if __name__ == '__main__':
    pass
