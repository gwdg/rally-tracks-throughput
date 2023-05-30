import argparse
import binascii
import json
import os
import re
import sys
import time

from dataclasses import dataclass

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from pyope.ope import OPE, ValueRange

# Since we decode YYYY-mm-dd to YYYYmmdd
# this can map everything up to year 3000, which should be plenty enough
DATE_MIN_RANGE = 0 # i.e below 0000-00-01
DATE_MAX_RANGE = 30000000 # i.e. above 2999-12-31

@dataclass
class EncryptionSettings:
    encrypt_keys: bool
    ope_key: bytes
    aes_key: bytes
    aes_iv: bytes

# BASIC ENCRYPTION BUILDING BLOCKS
def _encrypt_aes(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return binascii.hexlify(ciphertext).decode()

def _decrypt_aes(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(binascii.unhexlify(ciphertext))
    return unpad(decrypted, AES.block_size).decode()

def _encrypt_ope(n, key, min_range, max_range):
    return OPE(key, in_range=ValueRange(min_range, max_range)).encrypt(n)

def _decrypt_ope(n, key, min_range, max_range):
    return OPE(key, in_range=ValueRange(min_range, max_range)).decrypt(n)

# ACTUAL ENCRYPTION METHODS
def encrypt_key(settings, plaintext):
    return encrypt_str(settings, plaintext)

def encrypt_str(settings, plaintext):
    return _encrypt_aes(plaintext, settings.aes_key, settings.aes_iv)

def encrypt_int(settings, attrs, plaintext):
    min_range = attrs["min_range"]
    max_range = attrs["max_range"]
    ope_key = settings.ope_key
    return _encrypt_ope(plaintext, ope_key, min_range, max_range)
    ...

def encrypt_float(settings, attrs, plaintext):
    min_range = attrs["min_range"]
    max_range = attrs["max_range"]
    step = attrs["step"]
    ope_key = settings.ope_key

    converted_to_int = map_float_to_int(min_range, max_range, step, plaintext)
    # (The min_range_converted would always be 0)
    max_range_converted = map_float_to_int(min_range, max_range, step, max_range)

    return _encrypt_ope(converted_to_int, ope_key, 0, max_range_converted)

def encrypt_date(settings, plaintext):
    ope_key = settings.ope_key

    converted_to_int = map_date_to_int(plaintext)

    return _encrypt_ope(converted_to_int, ope_key, DATE_MIN_RANGE, DATE_MAX_RANGE)

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

# Validation functions
def valid_file_or_die(path):
    if not os.path.isfile(path):
        print(f"\"{path}\" is not a valid path", file=sys.stderr)
        sys.exit(0)

def get_encryption_settings_or_die(metadata):
    try:
        encrypt_keys = metadata["settings"]["ENCRYPT_KEYS"]
    except KeyError:
        print("\"settings.ENCRYPT_KEYS\" key not found in JSON!", file=sys.stderr)
        sys.exit(1)
    try:
        ope_key = metadata["settings"]["OPE"]["key"]
    except KeyError:
        print("\"settings.OPE.key\" key not found in JSON!", file=sys.stderr)
        sys.exit(1)
    try:
        aes_key = metadata["settings"]["AES"]["key"]
    except KeyError:
        print("\"settings.AES.key\" key not found in JSON!", file=sys.stderr)
        sys.exit(1)
    try:
        aes_iv = metadata["settings"]["AES"]["iv"]
    except KeyError:
        print("\"settings.AES.iv\" key not found in JSON!", file=sys.stderr)
        sys.exit(1)
    return EncryptionSettings(
        encrypt_keys,
        ope_key.encode(),
        binascii.unhexlify(aes_key),
        binascii.unhexlify(aes_iv)
    )

# The main program functions
def encrypt_dict_based_on_metadata(settings, metadata, obj):
    res = {}
    # Now we want to encrypt each attribute according to the format defined in the metadata section
    # See the README for more information.
    for key in obj:
        # Value encryption
        key_attrs = metadata["attributes"][key]
        key_type = key_attrs["type"]
        val = obj[key]

        # TODO refactor me.
        if key_attrs.get("multi") != True:
            match key_type:
                case "str":
                    val = encrypt_str(settings, val)
                case "int":
                    val = encrypt_int(settings, key_attrs, val)
                case "float":
                    val = encrypt_float(settings, key_attrs, val)
                case "date":
                    val = encrypt_date(settings, val)
                case _:
                    print(f"Unknown keytype \"{key_type}\" for key \"{key}\"!", file=sys.stderr)
                    sys.exit(1)
        else:
            match key_type:
                case "str":
                    val = [encrypt_str(settings, x) for x in val]
                case "int":
                    val = [encrypt_int(settings, key_attrs, x) for x in val]
                case "float":
                    val = [encrypt_float(settings, key_attrs, x) for x in val]
                case "date":
                    val = [encrypt_date(settings, x) for x in val]
                case _:
                    print(f"Unknown keytype \"{key_type}\" for key \"{key}\"!", file=sys.stderr)
                    sys.exit(1)

        # Key encryption
        if settings.encrypt_keys:
            key = encrypt_key(settings, key)
        res[key] = val
    return res
    ...

def main(encrypted_file, corpus_file):
    # Verify the files
    valid_file_or_die(encrypted_file)
    valid_file_or_die(corpus_file)

    # Parse and use the metadata dict
    with open(encrypted_file, 'r') as fp:
        metadata = json.load(fp)
    settings = get_encryption_settings_or_die(metadata)
    encrypt = lambda obj: encrypt_dict_based_on_metadata(settings, metadata, obj)

    # Encrypted corpus Output path
    # For now, lets just put it in the current dir
    output_path = f"./index_{int(time.time())}.json"

    # The corpus file is formatted as one JSON object per line.
    # It is not wrapped into a big JSON array
    # So we can easily stream over it
    with open(corpus_file, 'r') as input_file:
        with open(output_path, 'w') as output_file:
            for line in input_file:
                if not line.strip():
                    continue

                # The actual work
                obj = json.loads(line)
                print(line)
                encrypted_obj = encrypt(obj)
                output_file.write(json.dumps(encrypted_obj) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encryptes corpora for rally benchmarks")
    parser.add_argument("index_encrypted", help="Path to encrypted JSON metadata file")
    parser.add_argument("corpus_file", help="Path to corpus JSON file")
    args = parser.parse_args()
    if not args.index_encrypted or not args.corpus_file:
        parser.error("Both encrypted and corpus files must be provided.")

    main(args.index_encrypted, args.corpus_file)
