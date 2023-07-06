import argparse
import binascii
import json
import os
import sys
import time

from dataclasses import dataclass

from encryption_methods import encrypt_key, encrypt_str, encrypt_int, encrypt_date, encrypt_float, encrypt_time

@dataclass
class EncryptionSettings:
    encrypt_keys: bool
    ope_key: bytes
    aes_key: bytes
    aes_iv: bytes


def file_len(filename):
    i = 0
    with open(filename, 'r') as fp:
        for _ in fp:
            i+=1
    return i

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
                case "time":
                    val = encrypt_time(settings, val)
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

def main(encrypted_file, corpus_file):
    # Verify the files
    valid_file_or_die(encrypted_file)
    valid_file_or_die(corpus_file)

    # Parse and use the metadata dict
    with open(encrypted_file, 'r') as fp:
        metadata = json.load(fp)
    settings = get_encryption_settings_or_die(metadata)

    # Encrypted corpus Output path
    # For now, lets just put it in the current dir
    output_path = corpus_file.replace(".json", "_encrypted.json")

    # The corpus file is formatted as one JSON object per line.
    # It is not wrapped into a big JSON array
    # So we can easily stream over it
    i = 0
    n = file_len(corpus_file)
    with open(corpus_file, 'r') as input_file:
        with open(output_path, 'w') as output_file:
            for line in input_file:
                if not line.strip():
                    continue

                # Show that something happens
                print(f"Line {i}/{n}")
                i+=1

                # The actual work
                obj = json.loads(line)
                encrypted_obj = encrypt_dict_based_on_metadata(settings, metadata, obj)
                output_file.write(json.dumps(encrypted_obj) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encryptes corpora for rally benchmarks")
    parser.add_argument("index_encrypted", help="Path to encrypted JSON metadata file")
    parser.add_argument("corpus_file", help="Path to corpus JSON file")
    args = parser.parse_args()
    if not args.index_encrypted or not args.corpus_file:
        parser.error("Both encrypted and corpus files must be provided.")

    main(args.index_encrypted, args.corpus_file)
