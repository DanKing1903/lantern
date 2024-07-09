import typing
from decimal import Decimal
from typing import SupportsFloat, TypeAlias

import numpy as np

Numeric: TypeAlias = SupportsFloat


def convert_numpy(val: typing.Any) -> typing.Any:
    if isinstance(val, np.integer):
        return int(val)
    if isinstance(val, np.floating):
        return float(val)
    return val
