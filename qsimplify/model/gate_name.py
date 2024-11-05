from enum import Enum

class GateName(Enum):
    ID = "id"
    H = "h"
    X = "x"
    Y = "y"
    Z = "z"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    MEASURE = "measure"
    SWAP = "swap"
    CH = "ch"
    CX = "cx"
    CZ = "cz"
    CSWAP = "cswap"
    CCX = "ccx"
    BARRIER = "barrier"

    @classmethod
    def from_str(cls, name: str):
        try:
            return cls(name.lower())
        except ValueError:
            raise ValueError(f"'{name}' is not a valid GateName")
