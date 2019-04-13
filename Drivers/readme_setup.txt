2015-01-14 Peter Maerki

Install compact_2012 with labber on windows 7

Visa Driver: (is used by labber)
http://www.ni.com/download/ni-visa-5.2/3337/en/ -> visa520full.exe

Uncheck all but NI-VISA 5.2/Run Time Support/USB

ni 8452 driver (NI USB to SPI card)
http://www.ni.com/download/ni-845x-15.0/5611/en/ -> NI-845x_1500.exe

Uncheck: all but NI-VISA 15.0/Run Time Support/USB
Uncheck: Disable fast startup

Set ID to NI 8452 card:
Startmenu PC: NI MAX: 
Geräte und Schnittstellen
find NI USB-8452
Tab unten General
Set Name: "8452"
save

labber instrument driver
add
ETH Voltage Source compact_2012
Interface: Other
Adress: 8452


