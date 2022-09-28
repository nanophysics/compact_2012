# Installation of Labber Driver for heater_thermometrie_2021

**IMPORTANT** This document describes the installation for these projects

Please note that this installation also installs the required python packages for the `pyboard` and `pyvisa`.

| Python | Labber | Other Modules |  Project |
| - | - | - | - |
| 3.7 | yes | pyboard | [heater_thermometrie_2021](https://github.com/nanophysics/heater_thermometrie_2021/blob/main/doc_installation/README_INSTALLATION_python3_7_9.md) |
| 3.7 | yes | pyboard | [compact_2012](https://github.com/nanophysics/compact_2012/blob/master/doc_installation/README_INSTALLATION_WITH_LABBER.md) |
| 3.7 | yes | pyvisa | [labber_AMI430](https://github.com/nanophysics/labber_AMI430) |



## Pathnames

Tag | Default | Comment
-- | -- | --
`<LABBERDIR>` | `C:\Program Files\Labber` | Labber installation directory
`<LABBERPY32>` | `C:\Program Files\Labber\python-labber-32` | Labber Python 32 bit
`<LABBERPY64>` | `C:\Program Files\Labber\python-labber` | Labber Python 64 bit
`<LABBERDRIVERS>` | `C:\Program Files\Labber\Drivers` | Labber drivers
`<LABBERLOCALDRIVERS>` | `C:\Users\maerki\Labber\Drivers` | Labber local drivers. `maerki` is the logged in user
`<GITBIN>` | `C:\Program Files\Git\bin` | Git binaries

Mapping Tag to Labber Preferences

Tag        | Labber Instrument Server, Menu Preferences
-- | --
`<LABBERDIR>` | Tab Advanced, Application Folder
`<LABBERDRIVERS>` | Tab Folders, Instrument Drivers
`<LABBERLOCALDRIVERS>` | Tab Folders, Local Drivers



## Installation of Python 3.7.9 64bit
https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe
Windows 64bit msi installer
 - Uncheck: Install launcher for all users (recommended)
 - Uncheck: Add Python 3.7 to path
 - Customize installation
   - Check: Documentation
   - Check: pip
   - Uncheck: tcl/tk and IDLE
   - Uncheck: Python test suite
   - Uncheck: pylauncher
   - Uncheck: for all users
 - Advanced
   - Uncheck: Install for all users
   - Uncheck: ALL OTHER OPTIONS
   - `C:\Users\maerki\AppData\Local\Programs\Python\Python37`


### Installation of Labber 1.7.7

Install Labber using the installer

### Configure Labber to use Python 3.7.9

Labber Instrument Server Window -> Edit -> Preferences -> Advanced -> Python distribution -> `C:\Users\maerki\AppData\Local\Programs\Python\Python37\python.exe`


### Git installation

[README_INSTALLATION_git.md](README_INSTALLATION_git.md)

## Install heater_thermometrie_2021 labber driver

### Clone git repository

Run `cmd.exe`:
```bash
cd C:\Users\maerki\Labber\Drivers
git clone https://github.com/nanophysics/heater_thermometrie_2021
cd heater_thermometrie_2021

- or -

git clone https://github.com/nanophysics/compact_2012
cd compact_2012
```

### Install python requirements

Run `cmd.exe` below as **Administrator**.
```bash
cd <project>

"C:\Users\maerki\AppData\Local\Programs\Python\Python37\python.exe" -m pip install --upgrade pip
"C:\Users\maerki\AppData\Local\Programs\Python\Python37\python.exe" -m pip install -r requirements.txt -r requirements_development.txt
```

There will be some warnings about *PATH*. You may ignore them.

The last line should be `Successfully installed ... mpfshell2-100.9.xx ...`!


## Configure the heater_thermometrie_2021 in the Labber Instrument Server

Start the Labber Instrument Server and choose menu `Edit -> Add...`

![LABBER ADD](images/installation_labber_add.png "LABBER ADD")

## Update the heater_thermometrie_2021 driver and calibration data

The driver AND the calibration data is stored in the git repository located at `<LABBERLOCALDRIVERS>\heater_thermometrie_2021`.

Double click `<LABBERLOCALDRIVERS>\heater_thermometrie_2021\run_git_pull.bat` to pull the newest version.
