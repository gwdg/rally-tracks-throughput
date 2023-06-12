import binascii

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from pyope.ope import OPE, ValueRange

from conversion_algorithms import map_float_to_int, map_date_to_int, map_time_to_int

# Since we decode YYYY-mm-dd to YYYYmmdd
# this can map everything up to year 3000, which should be plenty enough
DATE_MIN_RANGE = 0 # i.e below 0000-00-01
DATE_MAX_RANGE = 30000000 # i.e. above 2999-12-31
# Analagously with YYYY-mm-dd hh:mm:ss
TIME_MIN_RANGE = 0
TIME_MAX_RANGE = 30000000000000

MIN_OUT_RANGE = 0
MAX_OUT_RANGE = 2**64-1


def _encrypt_aes(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return binascii.hexlify(ciphertext).decode()

def _decrypt_aes(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(binascii.unhexlify(ciphertext))
    return unpad(decrypted, AES.block_size).decode()

def _encrypt_ope(n, key, min_range, max_range):
    return OPE(key, in_range=ValueRange(min_range, max_range), out_range=ValueRange(MIN_OUT_RANGE, MAX_OUT_RANGE)).encrypt(n)

def _decrypt_ope(n, key, min_range, max_range):
    return OPE(key, in_range=ValueRange(min_range, max_range), out_range=ValueRange(MIN_OUT_RANGE, MAX_OUT_RANGE)).decrypt(n)

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
    min_range_converted = map_float_to_int(min_range, max_range, step, min_range)
    max_range_converted = map_float_to_int(min_range, max_range, step, max_range)

    return _encrypt_ope(converted_to_int, ope_key, min_range_converted, max_range_converted)

def encrypt_date(settings, plaintext):
    ope_key = settings.ope_key

    converted_to_int = map_date_to_int(plaintext)

    return _encrypt_ope(converted_to_int, ope_key, DATE_MIN_RANGE, DATE_MAX_RANGE)

def encrypt_time(settings, plaintext):
    ope_key = settings.ope_key

    converted_to_int = map_time_to_int(plaintext)

    return _encrypt_ope(converted_to_int, ope_key, TIME_MIN_RANGE, TIME_MAX_RANGE)

