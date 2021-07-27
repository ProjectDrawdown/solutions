"""Conversion module.

Provides useful conversions for the following:
    energy conversions
    volume conversions
    mass conversions
    distance conversions
    land area conversions
    inflation-adjusted-dollars
"""


from abc import ABC, abstractmethod


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


class Conversion(ABC):
    """
    A base-class that all conversion classes can inherit from.
    For each class, need to define the accepted names, the base unit,
    and the conversion rates to and from this base unit.

    Convert units from one form 'convert_from' to another 'convert_to'.
       Can specify the quantity of units to convert but defaults to one.
       Must be in the specified list 'accepted_names'
            convert_from : the starting units to be converted
            convert_to : the resulting units after the conversion
            quantity : the amount of units you have to begin with
    """

    def __init__(self, convert_from, convert_to, quantity=1):
        self.convert_from = convert_from
        self.convert_to = convert_to
        self.quantity = quantity
        self._converted_quantity = None

    @property
    @abstractmethod
    def accepted_names(self):
        pass

    @property
    @abstractmethod
    def _base_unit(self):
        pass

    @property
    @abstractmethod
    def conversion_rates(self):
        pass

    def __call__(self, quantity=1):
        return self.converted_quantity * quantity

    @property
    def convert_from(self):
        return self._convert_from

    @convert_from.setter
    def convert_from(self, unit_name):
        self.test_accepted_unit(unit_name)
        self._convert_from = unit_name

    @property
    def convert_to(self):
        return self._convert_to

    @convert_to.setter
    def convert_to(self, unit_name):
        self.test_accepted_unit(unit_name)
        self._convert_to = unit_name

    @property
    def converted_quantity(self):
        if self._converted_quantity is None:
            self._converted_quantity = self.convert_units()
        return self._converted_quantity

    def test_accepted_unit(self, unit_name):
        if unit_name not in self.accepted_names:
            raise ValueError(
                f'The supplied unit name {unit_name} is not an accepted '
                f'unit name. Accepted names are {self.accepted_names}')

    def convert_units(self):
        """
        Converts {self.convert_from} to the base unit first {self._base_unit}.
        Then converts that to the final unit {self.convert_to}

        """
        if self.convert_from == self.convert_to:
            return self.quantity
        base_key_to_search = f'{self.convert_from}_to_{self._base_unit}'
        conversion_key_to_search = f'{self._base_unit}_to_{self.convert_to}'
        base_unit_quantity = self.conversion_rates.get(base_key_to_search)
        conversion_rate = self.conversion_rates.get(
            conversion_key_to_search)
        return self.quantity * conversion_rate * base_unit_quantity


class EnergyConversion(Conversion):
    """
    Convert between 'tj', 'gcal', 'mtoe', 'mbtu', 'gwh', 'twh', 'kwh'
    Source: http://www.iea.org/statistics/resources/unitconverter/
    """
    @property
    def accepted_names(self):
        return ('tj', 'gcal', 'mtoe', 'mbtu', 'gwh', 'twh', 'kwh')

    @property
    def _base_unit(self):
        return 'tj'

    @property
    def conversion_rates(self):
        return {
        'tj_to_tj': 1,
        'gcal_to_tj': 0.004187,
        'mtoe_to_tj': 41_868,
        'mbtu_to_tj': 0.001055,
        'gwh_to_tj': 3.6,
        'twh_to_tj': 3_600,
        'kwh_to_tj': 3.60E-06,
        'tj_to_gcal': 238.845897,
        'tj_to_mtoe': 0.000024,
        'tj_to_mbtu': 947.817120,
        'tj_to_gwh': 0.277778,
        'tj_to_twh': 0.000278,
        'tj_to_kwh': 277_777.778
    }


class VolumeConversion(Conversion):
    """
       Convert between U.S gallon ('gal_us'), U,K gallon ('gal_uk',)
       Barrel ('bbl'), Cubic foot ('cubic_ft'), litre('l'),
       Cubic meter ('cubic_m')
       Source: http://www.iea.org/statistics/resources/unitconverter/
    """

    @property
    def accepted_names(self):
        return ('gal_us', 'gal_uk', 'bbl', 'cubic_ft', 'l', 'cubic_m')

    @property
    def _base_unit(self):
        return 'gal_us'

    @property
    def conversion_rates(self):
        return {
            'gal_us_to_gal_us': 1,
            'gal_uk_to_gal_us': 1.20095,
            'bbl_to_gal_us': 42,
            'cubic_ft_to_gal_us': 7.48052,
            'l_to_gal_us': 0.26417,
            'cubic_m_to_gal_us': 264.17205,
            'gal_us_to_gal_uk': 0.83267,
            'gal_us_to_bbl': 0.02381,
            'gal_us_to_cubic_ft': 0.13368,
            'gal_us_to_l': 3.78541,
            'gal_us_to_cubic_m': 0.00379
        }


class MassConversion(Conversion):
    """
        Convert between gram ('g'), kilogram ('kg') and tonne ('t')
        """

    @property
    def accepted_names(self):
        return ('g', 'kg', 't')

    @property
    def _base_unit(self):
        return 'kg'

    @property
    def conversion_rates(self):
        return {
            'kg_to_kg': 1,
            'g_to_kg': 1e-3,
            't_to_kg': 1e3,
            'kg_to_g': 1e3,
            'kg_to_t': 1e-3
        }


class DistanceConversion(Conversion):
    """
        Convert between miles ('mi') and kilometres ('km')
        """

    @property
    def accepted_names(self):
        return ('mi', 'km')

    @property
    def _base_unit(self):
        return 'km'

    @property
    def conversion_rates(self):
        return {
            'km_to_km': 1,
            'km_to_mi': 0.621371,
            'mi_to_km': 1.609344
        }
