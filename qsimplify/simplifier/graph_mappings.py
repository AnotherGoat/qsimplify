"""Contains a data structure that stores graph replacement mappings."""

from qsimplify.model import Position

type GraphMappings = dict[Position, Position]
"""A dictionary of position pairs, where the key is the original position and the value is the new position."""
