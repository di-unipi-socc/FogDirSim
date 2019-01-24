import random
from math import sqrt

def compute(ranges, values):
    number_iter = 20000
    sum = 0
    sampling = []
    for i in range(0, number_iter):
        r = random.random()
        for counter, prob in enumerate(ranges):
            if r <= prob:
                value = values[counter]
                sum += value
                sampling.append(value)
                break
    mean = sum / number_iter
    sampling_square = map(lambda x: (x-mean)**2, sampling)
    sum = 0
    for i in sampling_square:
        sum += i
    variance = sqrt(sum/number_iter)

    print("mean", mean, "variance", variance)

print("Device1 - CPU")
compute([0.2, 1], [100, 200])
print("Device1 - MEM")
compute([0.1, 0.2, 1], [15, 32, 64])
print()
print("Device2 - CPU")
compute([0.1, 1], [100, 200])
print("Device2 - MEM")
compute([0.1, 0.2, 0.4, 1], [32, 64, 96, 128])
print()
print("Device3 - CPU")
compute([0.2, 0.5, 1], [200, 300, 400])
print("Device3 - MEM")
compute([0.1, 0.2, 1], [64, 96, 128])