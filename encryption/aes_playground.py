import sys

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# NOTE THAT IT IS NOT SECURE TO FIX THE IV AND CIPHER
# In practise, one should use Crypto.Random.get_random_bytes
key = b'v\x0eX\x14\xb4{\xab\x90gL~\x9b\x93\x8a\xce!\xf0\x87zBx\xe4\r,\x15\xeb\xa6\xa3;%\xcdf'
iv = b':]W\xce\xcd`f\xe1\x06t\xc5F\xab\xa3G\xad'

def _encrypt(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return ciphertext
encrypt = lambda plaintext : _encrypt(plaintext, key, iv)

def _decrypt(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    return unpad(decrypted, AES.block_size).decode()
decrypt = lambda plaintext : _decrypt(plaintext, key, iv)

if __name__ == "__main__":
    input_string = sys.argv[1] if len(sys.argv) == 2 else "default"
    print("Input:", input_string)
    encrypted1 = encrypt(input_string)
    encrypted2 = encrypt(input_string)
    print("Encrypted 1:", encrypted1)
    print("Encrypted 2:", encrypted2)
    decrypted1 = decrypt(encrypted1)
    decrypted2 = decrypt(encrypted2)
    print("Decrypted 1:", decrypted1)
    print("Decrypted 2:", decrypted2)
