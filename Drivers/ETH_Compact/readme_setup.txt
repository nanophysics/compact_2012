2019-04-13 Hans Maerki

Install compact_2012 with labber on windows 10

Windows: Install Visa Driver
----------------------------
http://www.ni.com/download/ni-visa-18.5/7973/en/ -> NIVISA1850full.exe

  Run as Administrator: NIVISA1850full.exe
  Leave default settings
  In Feature Dialog:
    Uncheck everything
    Check: NI-VISA 18.5 -> Runtime Support
    Check: NI Measurement & Automation Explorer 18.5
  Check: Disable Windows fast startup


Windows: Install Driver for SPI Card
------------------------------------
ni 8452 driver (NI USB to SPI card)
http://www.ni.com/download/ni-845x-18.0/7601/en/ -> NI-845x_1800.exe

  Run as Administrator: NI-845x_1800.exe
  Leave default settings
  In Feature Dialog:
    Uncheck everything
    Check: NI-845x Driver 18.0 -> LabWindows/CVI Support
    Check: NI-845x Driver 18.0 -> LabWindows/CVI Support -> Examples
  Check: Disable Windows fast startup

Windows: Install labber
-----------------------

NI Max: Configure Name for SPI Card
-----------------------------------
Set ID to NI 8452 card:
Startmenu PC: NI MAX: 
Geräte und Schnittstellen
find NI USB-8452
Tab unten General
Set Name: "compact2012-A"
save

Labber Instrument Server: Configure
-----------------------------------
add
ETH Voltage Source compact_2012
Interface: Other
Adress: compact2012-A
check: "run in 32-bit mode" (in "Show advanced interface settings")

