"""Conversion module.

Provides useful conversions for the following:
    energy conversions
    volume conversions
    mass conversions
    distance conversions
    land area conversions
    inflation-adjusted-dollars
"""


def mha_to_ha(mha=1):
    """Convert mega hectares to hectares
        mha : the number of mega hectares
    """
    return mha * 10**6


def terawatt_to_kilowatt(tw=1):
    """Convert terawatts to kilowatts
        tw : the number of terawatt hours
      """
    return tw * 10**9
