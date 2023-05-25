import sys

from pyope.ope import OPE

# NOTE THAT IT IS NOT SECURE TO FIX THE KEY
# in practise, one should use pyope.ope.OPE.generate_key()
key = b'cJ2x4CY+e9+Egi29p0Db9b4iz3woTnTHaX9OX7BRdWc='
cipher = OPE(key)

encrypt = cipher.encrypt
decrypt = cipher.decrypt

if __name__ == "__main__":
    input_string = sys.argv[1] if len(sys.argv) == 2 else "123"
    n = int(input_string)
    print("Input:", n)
    encrypted1 = encrypt(n)
    encrypted2 = encrypt(n)
    print("Encrypted 1:", encrypted1)
    print("Encrypted 2:", encrypted2)
    decrypted1 = decrypt(encrypted1)
    decrypted2 = decrypt(encrypted2)
    print("Decrypted 1:", decrypted1)
    print("Decrypted 2:", decrypted2)

assert encrypt(1000) < encrypt(2000) < encrypt(3000)
assert decrypt(encrypt(1337)) == decrypt(encrypt(1337))
