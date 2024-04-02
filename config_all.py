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



ConfigCompact2012('20121111_01',
  HARDWARE_VERSION='2012',
  COMMENT='compact_2012_da'
  # Very first working compact, einige Korrekturen auf Leiterplatte.
  # HV_amplifier = False
  # Resolution_dac_12 = False
  # extension_left = ''
  # extension_right = ''
)

ConfigCompact2012('20140711_01',
  HARDWARE_VERSION='2014',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = False
  # extension_left = '20150811_07'
  # extension_right = '20150709_01'
)

ConfigCompact2012('20150530_10',
  HARDWARE_VERSION='2014',
  COMMENT='compact_2012_da'
  # HV_amplifier = False
  # Resolution_dac_12 = False
  # extension_left = ''
  # extension_right = ''
)

ConfigCompact2012('20150530_11',
  HARDWARE_VERSION='2014',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = False
  # extension_left = ''
  # extension_right = ''
)

ConfigCompact2012('20150530_12',
  HARDWARE_VERSION='2014',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = False
  # extension_left = ''
  # extension_right = ''
)

ConfigCompact2012('20150530_13',
  HARDWARE_VERSION='2014',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = False
  # extension_left = ''
  # extension_right = ''
)

ConfigCompact2012('20150530_14',
  HARDWARE_VERSION='2014',
  COMMENT='compact_2012_da'
  # HV_amplifier = True
  # Resolution_dac_12 = False
  # extension_left = ''
  # extension_right = ''
)

ConfigCompact2012('20190606_01',
  HARDWARE_VERSION='2019',
  COMMENT='Prototype for the Compact_2012 series of 2019'
)

ConfigCompact2012('20191217_09',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da_simplebox fuer Hansjuerg Schmutz'
)

ConfigCompact2012('20190606_02',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # HV_amplifier = Unknown
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_71',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, kein calib step, da_out -10V etwas grosse steps, urs_second'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_72',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, gut, wenig flicker, bigmom_first'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'compact_2012_iv_2015'
  # extension_right = 'compact_2012_iv_2015'
)

ConfigCompact2012('20200918_73',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, todo quality comment'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_74',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, SUPPLY_+14V etwas zu tief, akzept. urs_first'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_75',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, SUPPLY_+14V zappelt etwas aber ok'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_76',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, knapp ueber einigen rauschgrenzen aber ok'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_77',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, HV amp sometimes spikes, CH14 is the best'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'iv_2015 SN 20200511_40'
  # extension_right = 'iv_2015 SN 20200511_42'
)

ConfigCompact2012('20200918_78',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da,HV_OUT_DIR_+100V CH11 stepsize ueberschritten, aber ok, christian_odin'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'empty'
  # extension_right = 'empty'
)

ConfigCompact2012('20200918_79',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, SUPPLY_+14V rumpelt, aber ok'
  # sofia_first
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'iv_2015 SN 20200511_35'
  # extension_right = 'iv_2015 SN 20200511_36'
)

ConfigCompact2012('20200918_80',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da'
  # tabea_first
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'iv_2015 SN 20200511_37'
  # extension_right = 'iv_2015 SN 20200511_38'
)

ConfigCompact2012('20200918_81',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, SUPPLY_+14V rumpelt, CH11 etwas grosse steps aber ok, christian_loki'
  # HV_amplifier = True
  # Resolution_dac_12 = True
  # extension_left = 'compact_2012_iv_2015'
  # extension_right = 'compact_2012_iv_2015'
)

ConfigCompact2012('20200918_82',
  HARDWARE_VERSION='2020',
  COMMENT='compact_2012_da, kein calib step'
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
  COMMENT='compact_2012_da, SUPPLY_+14V noise, aber ok, bigmom_second'
  # HV_amplifier = False
  # Resolution_dac_12 = True
  # extension_left = 'compact_2012_iv_2015'
  # extension_right = 'compact_2012_iv_2015'
)