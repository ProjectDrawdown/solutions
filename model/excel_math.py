import math



def round(x):
    is_neg = False;

    # Excel rounds away from zero, so 1.5 rounds to 2 and -1.5 rounds to -2.
    if x < 0.0:
        is_neg = True
        x = math.fabs(x)

    # Determine the value rounded down, then add 0.5 to it. This won't be exactly 0.5
    # due to floating point precision, but we're just going to compare the argument to it.
    # If less than the halfway point, round down.
    halfway = math.floor(x) + 0.5
    x = math.floor(x) if x < halfway else math.ceil(x)
    if is_neg:
        x = -x
    return int(x)
