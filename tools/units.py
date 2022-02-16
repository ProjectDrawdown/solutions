"""Units of measure that are used in solutions

Dimensions of SI units are re-used.
"""

from fractions import Fraction
from unitsofmeasure import decprefix, PREFIX_1, SCALAR, Unit, UnitMap
from unitsofmeasure.base import kg

_FRACTION_1K = Fraction(1000, 1)

# mass
Gt = Unit("Gt", "gigatonne", kg.dimension, decprefix.G, _FRACTION_1K)
Mt = Unit("Mt", "megatonne", kg.dimension, decprefix.M, _FRACTION_1K)
kt = Unit("kt", "kilotonne", kg.dimension, decprefix.k, _FRACTION_1K)

# scalar
ppm = Unit("ppm", "parts per million", SCALAR, PREFIX_1, Fraction(1, 1_000_000))
ppb = Unit("ppb", "parts per billion", SCALAR, PREFIX_1, Fraction(1, 1_000_000_000))

unit_map = UnitMap() # instantiate our own default unit map

# re-implemented here to use our own default map
def map_to_unit(unit: Unit, map: UnitMap = unit_map): # -> ((o: object) -> object) requires Python 3.11
    """Decorate functions or classes with units."""
    def wrap(o: object) -> object:
        map.set(o, unit)
        return o
    return wrap

# re-implemented here to use our own default map
def set_unit(o: object, unit: Unit, map: UnitMap = unit_map) -> None:
    """Set unit of object in map."""
    return map.set(o, unit)

# re-implemented here to use our own default map
def get_unit(o: object, map: UnitMap = unit_map) -> Unit:
    """Get unit of object from map."""
    return map.get(o)
