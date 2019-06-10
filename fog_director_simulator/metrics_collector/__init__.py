from functools import lru_cache
from functools import wraps
from random import gauss as normal
from typing import Any
from typing import Callable
from typing import TypeVar

import scipy.stats as stats
from numpy.random import choice
from scipy.stats._continuous_distns import truncexpon_gen
from sqlalchemy.exc import SQLAlchemyError
# from numpy.random import normal

Func = TypeVar('Func', bound=Callable[..., Any])


@lru_cache(maxsize=256)
def get_scipy_truncnorm(mean: float, std_deviation: float, lower_bound: float, upper_bound: float) -> truncexpon_gen:
    return stats.truncnorm(
        (lower_bound - mean) / std_deviation, (upper_bound - mean) / std_deviation, loc=mean, scale=std_deviation)


def random_sample(mean: float, std_deviation: float, lower_bound: float, upper_bound: float) -> float:
    if lower_bound == upper_bound:
        return lower_bound
    sample = normal(mean, std_deviation)
    while not (lower_bound < sample < upper_bound):
        sample = normal(mean, std_deviation)
    return sample
    # return get_scipy_truncnorm(mean, std_deviation, lower_bound, upper_bound).rvs()


def random_flag(probability_of_true: float) -> bool:
    return choice((True, False), p=(probability_of_true, 1 - probability_of_true))


class ignore_sqlalchemy_exceptions:
    default_return_value: float

    def __init__(self, default_return_value: float):
        self.default_return_value = default_return_value

    def __call__(self, fun: Func) -> Func:
        @wraps(fun)
        def wrapper(*args: Any, **kwargs: Any) -> float:
            try:
                return fun(*args, **kwargs)
            except SQLAlchemyError as exc:
                print(f'{fun.__module__}.{fun.__name__} failed with {repr(exc)}, returning default_value={self.default_return_value}')
                return self.default_return_value

        return wrapper  # type: ignore
