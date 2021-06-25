
# DAC longterm: Deliver sample data and observe using afterglow

There must NOT be any signal on channel 1 and 2 around 0V, 10V, -10V.

```
for i in range(10000000):
    if i % 1000 == 0:
        print(i)
    f_DA1 = random.uniform(4.5, 5.5)
    f_DA2 = random.uniform(-4.5, -5.5)
    f_DAx = random.uniform(-10.0, 10.0)
    d = {}
    for i, f in enumerate((f_DA1, f_DA2, f_DAx, f_DAx, f_DAx, f_DAx, f_DAx, f_DAx, f_DAx, f_DAx)):
        d[i] = {'f_DA_OUT_desired_V': f,}
    driver.sync_dac_set_all(d)
```

# Labber: Keep the signal in error conditions

- A signal is set in labber: channel 1: 6V
- The tests must show, that this signal never changes (for not destroying the sample)

Measurement Editor

- DA1: 4.5V..5.5V, 101 measurements
- DA2: -5.5V..-4.5V, 5000 measurements

## Disconnect pyboard USB

- Unplug: Labber "Timeout error". "compact_2012 instrument stopped'
- Manual: Labber "Start Measurement"

==> OK

## Shut down Labber "Measurement Editor"

==> OK

## Shut down Labber "Instrument Server"

==> OK

## Shut down Labber compact_2012 process

==> OK

## Unplug 40 pol cable betweet pyboard and compact_2012

==> Spikes on DAx
==> driver survives

# Power off compact2012

==> Spikes on DAx
==> driver survives


