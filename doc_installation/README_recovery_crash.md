# Recovery after a labber crash

When Labber Instrument Server starts, the output voltages of compact may
be initialized to 0V.

However, this might not be desired when recovering after Labber crashed in the middle of an experiment.

The goal is to apply the voltages which where active before Labber crashed.

## Start condition for this document

Labber crashed during an experiment. Labber Instrument server is stopped now.

## Preparation for recovery

In the labber driver folder of campact, there is a document `Values-xxx.txt` with the current voltages used by compact.

In this example, it holds the values

```
2023-04-27_08:56:58
compact_2012
While measuring with Labber, this file is written every 5.0 seconds. If you delete this file, Labber will write it again.
When Labber crashes and the instrument server loses the values, you may manually copy and paste the values from this file to the instrument server config. Set cfg. Then start instrument server.
Voltages: physical values in volt; the voltage at the OUT output.

DA1 0.00000000 V     (range, jumper, +/- 10 V)
DA2 2.00000000 V     (range, jumper, +/- 10 V)
DA3 0.00000000 V     (range, jumper, +/- 10 V)
DA4 0.00000000 V     (range, jumper, +/- 10 V)
...
```

* Make a backup copy of this file as it will be overwritten later!

Start Labber Instrument Server, but not the compact driver!

* Right-mouse click on the Compact Driver -> `Config...`
* At startup: `Set config`
* Enter the values from `Values-xxx.txt` above. In our example:
  * DA2-voltage: `2`  

## Start driver

* Button `Start Instrument` on the compact Driver

This will write the voltages again from Labber to compact 2012.

## Continue experiment

Now you may continue the experiment in the `Experiment Editor`. Make sure that the experiment starts with given the voltages.
