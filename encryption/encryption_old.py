import json
import re
import sys
from datetime import datetime
from enum import Enum
from functools import partial

# From pycryptodome
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

# From pyope
from pyope.ope import OPE, ValueRange

# BEGIN CONFIGURATION
# Do you also want to AES encrypt the keys?
ALSO_ENCRYPT_KEYS = True
START_INTERVAL = 0.00
END_INTERVAL = 10.00
STEP_SIZE = 0.01
# END CONFIGURATION

AES_IV = b'0123456789abcdef'
AES_KEY = get_random_bytes(32)
# Default ranges are (0, 2^15-1) and (0, 2^32-1)
OPE_KEY = OPE.generate_key()
OPE_CIPHER = OPE(OPE_KEY, in_range=ValueRange(0, 2**17-1), out_range=ValueRange(0, 2**34-1))

print("TYPE OF AES_KEY: ", type(AES_KEY))
print("TYPE OF OPE_KEY: ", type(OPE_KEY))
print("TYPE OF OPE_CIPHER: ", type(OPE_CIPHER))

def encrypt_AES_256(data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded_data = pad(data, cipher.block_size)
    ciphertext = cipher.encrypt(padded_data)
    #return AES_CIPHER.nonce, tag, ciphertext
    return ciphertext

def encrypt_OPE(integer):
    return OPE_CIPHER.encrypt(integer)

# Use partial application for less boilerplate
def map_float_to_int_generic(start, end, step, x):
    # Firstly some simple sanity checks
    if not (start <= x <= end):
        error_str = f"{x} is not in the interval [{start},{end}]! Unable to map..."
        print(error_str, file=sys.stderr)
        raise Exception(error_str)
    if (end-start) < step:
        error_str = f"Step size {step} is bigger than the interval [{start},{end}]!"
        print(error_str, file=sys.stderr)
        raise Exception(error_str) # TODO STEP 0

    # Next, we want to check whether the step size was chosen appropriately.
    # We know that
    # start + n * step = end
    # thus, we want to check whether n is an integer, i.e. the step size fits.
    n = (end-start)/step
    if not n.is_integer():
        error_str = f"Step size {step} is not valid for [{start},{end}]"
        print(error_str, file=sys.stderr)
        raise Exception(error_str)

    # Lastly, we want to find out whether the applied value is valid, i.e. whether it is exactly
    # on a step.
    # Note that this is not a strong requirement. If you want to fit query 1.23456, you should probably
    # set your step size to 10^-5, which is fair.
    # Just try to set your interval as small as possible as it obviously grows exponentially.
    #
    # Again, this means that n has to be a integer in
    # x = start + n * step
    n = (x-start)/step
    if not n.is_integer():
        error_str = f"{x} does not fit into [{start},{end}], step size {step}. Consider using a smaller step size"
        print(error_str, file=sys.stderr)
        raise Exception(error_str)
    return int(n)

map_float_to_int = partial(map_float_to_int_generic, START_INTERVAL, END_INTERVAL, STEP_SIZE)

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

def map_date_to_int2(date_string, reference_date='1900-01-01'):
    date = datetime.strptime(date_string, '%Y-%m-%d')
    reference_date = datetime.strptime(reference_date, '%Y-%m-%d')
    delta = date - reference_date
    return delta.days


class DataType(Enum):
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    DATE = "DATE"
    STRING = "STRING"
    UNKNOWN = "UNKNOWN"

def serialize_enum(enum_value):
    return enum_value.value

def deserialize_enum(enum_string):
    return DataType[enum_string]


def get_data_type(value):
    if isinstance(value, int):
        return DataType.INTEGER
    elif isinstance(value, float):
        return DataType.FLOAT
    elif isinstance(value, str):
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if date_pattern.match(value.strip()):
            return DataType.DATE
        else:
            return DataType.STRING
    else:
        return DataType.UNKNOWN


def encrypt_dict(d):
    result = {}
    for key, value in d.items():
        value_type = get_data_type(value)
        if ALSO_ENCRYPT_KEYS:
            key = encrypt_AES_256(key.encode('utf-8')).hex()
        if value_type == DataType.STRING:
            encrypted_value = encrypt_AES_256(value.encode('utf-8')).hex()
            result[key] = encrypted_value
        elif value_type == DataType.INTEGER:
            encrypted_value = encrypt_OPE(value)
            result[key] = encrypted_value
        elif value_type == DataType.FLOAT:
            encrypted_value = encrypt_OPE(map_float_to_int(value))
            result[key] = encrypted_value
            result[f"{key}_full"] = encrypt_AES_256(str(value).encode('utf-8')).hex()
        elif value_type == DataType.DATE:
            encrypted_value = encrypt_OPE(map_date_to_int(value))
            result[key] = encrypted_value
        else:
            print(f'Unknown data type: {value_type}', file=sys.stderr)
    return result

def map_keys(d):
    ret = []
    for key in d.keys():
        encrypted_key = encrypt_AES_256(key.encode('utf-8')).hex()
        ret.append(f"{key} -> {encrypted_key}")
    return "\n".join(ret)

def main(filename):
    # Print keys
    with open(filename, 'r') as file:
        first_line = file.readline()
        obj = json.loads(first_line)
        output = filename.replace('.json', '_keys.txt')
        with open(output, 'w') as output_file:
            output_file.write(map_keys(obj))
    # Main encryption
    with open(filename, 'r') as file:
        output = filename.replace('.json', '_encrypted.json')
        with open(output, 'w') as output_file:
            for line in file:
                if not line.strip():
                    continue
                obj = json.loads(line)
                encrypted_obj = encrypt_dict(obj)
                output_file.write(json.dumps(encrypted_obj) + "\n")

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
