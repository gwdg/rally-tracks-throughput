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
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
        # (this is string concat)
        num = year + month + day
        return int(num)
    else:
        raise ValueError('Invalid date format')

def map_time_to_int(time_string):
    time_pattern = re.compile(r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$')
    match = time_pattern.match(time_string)
    if match:
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
        hour = match.group(4)
        minute = match.group(5)
        second = match.group(6)
        # (This is string concat)
        num = year + month + day + hour + minute + second
        return int(num)
    else:
        raise ValueError('Invalid time format')
