import argparse
import binascii
import json

from encryption_methods import _encrypt_aes

def main(index_encrypted, index):
    # Getting the same keys from the file defining the encryption types
    with open(index_encrypted, 'r') as fp:
        metadata = json.loads(fp.read())
        aes_key = binascii.unhexlify(metadata["settings"]["AES"]["key"])
        aes_iv = binascii.unhexlify(metadata["settings"]["AES"]["iv"])

    # Getting the index.json
    with open(index, 'r') as fp:
        index_obj = json.loads(fp.read())

    # Encrypting each key of the index.json attributes
    props = index_obj["mappings"]["properties"]
    new_props = {}
    for p in props:
        value = props[p]
        p_enc = _encrypt_aes(p, aes_key, aes_iv)
        new_props[p_enc] = value
    index_obj["mappings"]["properties"] = new_props

    # Save the encrypted result
    with open("index_json_encrypted.json", 'w') as out:
        out.write(json.dumps(index_obj))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encryptes index.json for rally benchmarks")
    parser.add_argument("index_encrypted", help="Path to encrypted JSON metadata file")
    parser.add_argument("index", help="Path to the rally index.json")
    args = parser.parse_args()
    if not args.index_encrypted or not args.index:
        parser.error("Both encrypted and normal index files must be provided.")

    main(args.index_encrypted, args.index)
