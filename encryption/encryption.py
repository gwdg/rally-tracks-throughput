import argparse
import binascii
import functools
import json
import os
import sys
import time

from dataclasses import dataclass

@dataclass
class EncryptionSettings:
    encrypt_keys: bool
    ope_key: bytes
    aes_key: bytes
    aes_iv: bytes


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

def encrypt_dict_based_on_metadata(settings, metadata, obj):
    print(obj)
    res = {}
    # Now we want to encrypt each attribute according to the format defined in the metadata section
    # See the README for more information.
    for key in obj:
        # Key encryption
        if settings.encrypt_keys:
            ...

        # Value encryption
        key_attrs = metadata["attributes"][key]
        key_type = key_attrs["type"]
        match key_type:
            case "str":
                ...
            case "int":
                ...
            case "float":
                ...
            case "date":
                ...
            case _:
                print("")
    sys.exit(0)
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
    print(settings)

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

