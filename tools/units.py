"""Units of measure that are used in solutions

Dimensions of SI units are re-used.
"""

from fractions import Fraction
from unitsofmeasure import decprefix, no_prefix, scalar, Unit, UnitMap
from unitsofmeasure.base import kg

_fraction_1k = Fraction(1000, 1)

# mass
Gt = Unit("Gt", "gigatonne", kg.dimension, decprefix.G, _fraction_1k)
Mt = Unit("Mt", "megatonne", kg.dimension, decprefix.M, _fraction_1k)
kt = Unit("kt", "kilotonne", kg.dimension, decprefix.k, _fraction_1k)

# scalar
ppm = Unit("ppm", "parts per million", scalar, no_prefix, Fraction(1, 1_000_000))
ppb = Unit("ppb", "parts per billion", scalar, no_prefix, Fraction(1, 1_000_000_000))

unit_map = UnitMap()
