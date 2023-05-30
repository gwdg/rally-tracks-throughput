import re
import sys

# The underlying conversion algorithms
def map_float_to_int(min_range, max_range, step, x):
    # Firstly some simple sanity checks
    if not (min_range <= x <= max_range):
        error_str = f"{x} is not in the interval [{min_range},{max_range}]! Unable to map..."
        print(error_str, file=sys.stderr)
        sys.exit(1)
    if (max_range-min_range) < step:
        error_str = f"Step size {step} is bigger than the interval [{min_range},{max_range}]!"
        print(error_str, file=sys.stderr)
        sys.exit(1)

    # Next, we want to check whether the step size was chosen appropriately.
    # We know that
    # start + n * step = end
    # thus, we want to check whether n is an integer, i.e. the step size fits.
    n = (max_range-min_range)/step
    if not n.is_integer():
        error_str = f"Step size {step} is not valid for [{min_range},{max_range}]"
        print(error_str, file=sys.stderr)
        raise Exception(error_str)

    # Note that we allow the mapping to not completely fit. This is by design.
    # For example, if you just save some raw calculation done on doubles, you rarely
    # want to map with a precision of 10^16.
    # Thus, we just truncate it down.
    # The formula: x = start + n * step
    n = (x-min_range)/step
    return int(n)

def map_date_to_int(date_string):
    date_pattern = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')
    match = date_pattern.match(date_string)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        return year * 10000 + month * 100 + day
    else:
        raise ValueError('Invalid date format')
