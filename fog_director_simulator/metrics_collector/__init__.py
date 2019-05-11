import random
from functools import wraps
from typing import Any
from typing import Callable
from typing import TypeVar

from sqlalchemy.exc import SQLAlchemyError


Func = TypeVar('Func', bound=Callable[..., Any])


def random_sample(mean: float, std_deviation: float, lower_bound: float, upper_bound: float) -> float:
    sample = random.gauss(mean, std_deviation)
    while not (lower_bound < sample < upper_bound):
        sample = random.gauss(mean, std_deviation)
    return sample


def random_flag(probability_of_true: float) -> bool:
    random_value = random.randrange(start=0, stop=1)
    return random_value <= probability_of_true


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
                print(f'{fun.__module__}.{fun.__name__} failed with {exc}, returning default_value={self.default_return_value}')
                return self.default_return_value

        return wrapper  # type: ignore
