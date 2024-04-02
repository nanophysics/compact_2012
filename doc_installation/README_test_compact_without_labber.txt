# Use the compact driver without labber

## Simple, set voltage with comand line

advantage: simple
drawback: slow, approx 1s, depending on setup

cmd.exe
cd C:\data\temp\compact_2012        (for example, choose yourself)

Example, one compact_2012 only, searches the com port automatically

```python set_output.py DA1=-6.2```

Example, one or more compact_2012, com port defined and therefore faster.
You can find the com port in the device manager.

```python set_output.py DA4=0.333 DA5=0.533 DA10=9.976```

## Set voltages fast:
Write your own program, similar to set_output.py

Example:

```
...
def main():
    comport = "COM14"
    # Connect
    driver = compact_2012_driver.Compact2012(comport)
    while True:
        # ...
        dictVoltages = {\
        0: {'f_DA_OUT_desired_V': 7.333, 'f_gain': 1.0}, # 0: DA1\
        3: {'f_DA_OUT_desired_V': 3.333, 'f_gain': 1.0}, # 3: DA4\
        4: {'f_DA_OUT_desired_V': 5.533, 'f_gain': 1.0}}  # 4: DA5
        # Use dictionary to set 'f_DA_OUT_desired_V' and 'f_gain'
        driver.sync_dac_set_all(dictVoltages)
    driver.close()
```