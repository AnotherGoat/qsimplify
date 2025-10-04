"""Contains a data structure that stores graph pattern match mappings."""

from qsimplify.model import Position

type PatternMatch = dict[Position, Position]
"""A dictionary of position pairs, where the key is the position in the pattern and the value is the position in the graph."""
