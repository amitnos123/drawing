"""
Configuration objects for Meander components in GDS layouts.
Uses Pydantic for type validation and parameter encapsulation.
"""

from pydantic import BaseModel
from gdsfactory.typings import LayerSpec
from src.drawing.shared.utilities import DEFAULT_LAYER


class MeanderEulerConfig(BaseModel):
    """
    Configuration for the meander_euler function.
    """

    type: str = "meander_euler"
    wire_width: float = 0.2
    height: float = 10.0
    padding_length: float = 3.0
    spacing: float = 5.0
    num_turns: int = 9
    radius: float = 1.0
    layer: LayerSpec = DEFAULT_LAYER


class MeanderOptimalTurnConfig(BaseModel):
    """
    Configuration for the meander_optimal_turn function.
    """

    type: str = "meander_optimal_turn"
    wire_width: float = 0.2
    height: float = 10.0
    padding_length: float = 3.0
    spacing: float = 2.0
    num_turns: int = 9
