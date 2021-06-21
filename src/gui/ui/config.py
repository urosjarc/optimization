import sys
from typing import List

transperency: bool = True
ortogonalView: bool = False
lightPosition: List[float] = [10., 10., 100.]
birdsEye: int = 0
scaleRate: float = 0.
pointsSize: float = 10.0
ambientRate: float = .56
lightRate: float = .5
linesSize: float = 0.1
colormap: int = 0
light: bool = False

def getAll():
    d = {}
    # Set program config locations
    for name, val in sys.modules[__name__].__dict__.items(): # iterate through every module's attributes
        if name.count('__') != 2 and isinstance(val, (bool, list, int, float)):
            d[name] = val
    return d
