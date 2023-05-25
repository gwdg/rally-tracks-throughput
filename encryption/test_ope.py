# Does OPE support negative numbers?
from pyope.ope import OPE, ValueRange

key = b'cJ2x4CY+e9+Egi29p0Db9b4iz3woTnTHaX9OX7BRdWc='
cipher = OPE(key, in_range=ValueRange(-256, 2**10-1))

print("Test negative numbers")
x = cipher.encrypt(-48)
y = cipher.encrypt(-2)
z = cipher.encrypt(480)
print(x, y, z)
assert (x < y < z)
x = cipher.decrypt(x)
y = cipher.decrypt(y)
z = cipher.decrypt(z)
print(x, y, z)

print("test weird bounds")
cipher = OPE(key, in_range=ValueRange(31, 2**18-3482))
x = cipher.encrypt(35)
y = cipher.encrypt(482)
z = cipher.encrypt(88881)
print(x, y, z)
assert (x < y < z)
x = cipher.decrypt(x)
y = cipher.decrypt(y)
z = cipher.decrypt(z)
print(x, y, z)
