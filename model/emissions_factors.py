"""Emissions Factors module.

Conversions and lookups useful in converting to CO2 equivalents,
and other factors relating to emissions and pollutants.
"""

import enum

SOURCE = enum.Enum('SOURCE', 'AR5_WITH_FEEDBACK AR4 SAR')

class CO2Equiv:
  """Convert CH4/N2O/etc to equivalent CO2.

  conversion_source: which standard conversion model to follow:
     AR5 with feedback: value used in the IPCC 5th Assessment Report,
       as amended with feedback. This is the preferred selection.
     AR4: as used in the IPCC 4th Assessment Report.
     SAR: as used in the IPCC Second Assessment Report.
  """

  def __init__(self, conversion_source=None):
    self.conversion_source = conversion_source if conversion_source else SOURCE.AR5_WITH_FEEDBACK
    if self.conversion_source == SOURCE.AR5_WITH_FEEDBACK:
      self.CH4multiplier = 34
      self.N2Omultiplier = 298
    elif self.conversion_source == SOURCE.AR4:
      self.CH4multiplier = 25
      self.N2Omultiplier = 298
    elif self.conversion_source == SOURCE.SAR:
      self.CH4multiplier = 21
      self.N2Omultiplier = 310
    else:
      raise ValueError("invalid conversion_source=" + str(self.conversion_source))


def string_to_conversion_source(text):
  """Convert the text strings passed from the Excel implementation of the models
  to the enumerated type defined in this module."""
  if text == "AR5 with feedback":
    return SOURCE.AR5_WITH_FEEDBACK
  elif text == "AR5_with_feedback":
    return SOURCE.AR5_WITH_FEEDBACK
  elif text == "AR4":
    return SOURCE.AR4
  elif text == "SAR":
    return SOURCE.SAR
  else:
    raise ValueError("invalid conversion name=" + str(text))
