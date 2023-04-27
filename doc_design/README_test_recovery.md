# Hans Märki 2023-04-27

## Sequence tested

### Prepare values

* Install driver. Right Mouseclick on Driver -> `Config...`
* At startup: `Set config`
* DA1-voltage: `1`
* DA3-voltage: `3`

### Start driver

* Button `Start`
* On cmd window: 

    ***** f_values_plus_min_v=[1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`

**New value is written correctly**

### Set new voltage

* Close config dialog. Back to Instrument server.

* DA1-voltage: `-1`

* On cmd window: 

    ***** f_values_plus_min_v=[-1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

**New value is written correctly**
