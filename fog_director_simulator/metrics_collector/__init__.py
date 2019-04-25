import random


def random_sample(mean: float, std_deviation: float, lower_bound: float, upper_bound: float) -> float:
    sample = random.gauss(mean, std_deviation)
    while not (lower_bound < sample < upper_bound):
        sample = random.gauss(mean, std_deviation)
    return sample


def random_flag(probability_of_true: float) -> bool:
    random_value = random.randrange(start=0, stop=1)
    return random_value <= probability_of_true
