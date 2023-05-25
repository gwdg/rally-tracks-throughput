import binascii
import json

byte_string = b'v\x0eX\x14\xb4{\xab\x90gL~\x9b\x93\x8a\xce!\xf0\x87zBx\xe4\r,\x15\xeb\xa6\xa3;%\xcdf'
hex_string = binascii.hexlify(byte_string).decode('utf-8')
json_data = json.dumps({"array": hex_string})

json_obj = json.loads(json_data)
hex_output = json_obj["array"]
byte_output = binascii.unhexlify(hex_output)

print(byte_output)

assert byte_output == byte_string
