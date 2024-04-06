import numpy as np

def rnd(number):
    a = number // 10
    b = round(a / 5) * 5
    return b


print(rnd(271))

print(f"{np.gcd(6, 16)}")