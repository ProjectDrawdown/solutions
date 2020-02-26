import math


def round_away(x):
    """
    excel rounds away from zero on breakeven
    so 0.5 ==> 1.0, -0.5 ==> -1.0
    python2 does the same, hence this code
    copied almost verbatim from https://github.com/python/cpython/blob/master/Python/pymath.c#L71
    """
    absx = math.fabs(x)
    y = math.floor(absx)
    if absx - y >= 0.5:
        y += 1.0
    return int(math.copysign(y, x))
