#
# Compact_2012
#
# This file contains production-data of all Compact2012 which where produced.
#
SERIAL_UNDEFINED='SERIAL_UNDEFINED'
dict_compact2012 = {}

class ConfigCompact2012:
  def __init__(self, HWSERIAL, HARDWARE_VERSION, COMMENT):
    dict_compact2012[HWSERIAL] = self
    self.HWSERIAL = HWSERIAL
    self.HARDWARE_VERSION = HARDWARE_VERSION
    self.COMMENT = COMMENT

  def __repr__(self):
    return f'serial "{self.HWSERIAL}" with Hardware "{self.HARDWARE_VERSION}". {self.COMMENT}'

ConfigCompact2012(SERIAL_UNDEFINED,
  HARDWARE_VERSION='2019',
  COMMENT='Serial not defined, hardware unknown! Assuming a bare micropython board.'
)

ConfigCompact2012('20190606_01',
  HARDWARE_VERSION='2019',
  COMMENT='Prototype for the Compact_2012 series of 2019'
)

ConfigCompact2012('20191217_09',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da_simplebox fuer Hansjuerg Schmutz'
)

ConfigCompact2012('20200918_72',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_73',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_74',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_75',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_77',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_78',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_79',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_80',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_81',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_83',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, SUPPLY_+14V noise, aber ok'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_84',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, SUPPLY_+14V noise, aber ok'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)