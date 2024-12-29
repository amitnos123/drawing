"""
Meander component implementations for GDS layouts.
Provides different approaches to creating meander patterns.
"""

import gdsfactory as gf
import numpy as np
from itertools import chain
from gdsfactory.typings import LayerSpec
from src.drawing.shared.utilities import DEFAULT_LAYER, merge_decorator


@merge_decorator
@gf.cell
def meander_euler(
    wire_width: float = 0.2,
    height: float = 10,
    padding_length: float = 3,
    spacing: float = 5,
    num_turns: int = 9,
    radius: float = 1,
    layer: LayerSpec = DEFAULT_LAYER,
) -> gf.Component:
    """
    Creates a meandering wire pattern using smooth curves.

    Args:
        wire_width: Width of the wire.
        height: Total height of the meander.
        padding_length: Straight section length at inputs.
        spacing: Horizontal spacing between turns.
        num_turns: Number of turns in the meander.
        radius: Radius of curved sections.
        layer: Target GDS layer.

    Returns:
        gf.Component: Meander component.
    """
    c = gf.Component()

    points = _generate_meander_points(
        height=height,
        padding_length=padding_length,
        spacing=spacing,
        num_turns=num_turns,
    )

    path = gf.path.smooth(
        points, radius=radius, bend=gf.path.euler, use_eff=True, npoints=720, p=1
    )

    cross_section = gf.cross_section.strip(width=wire_width, layer=layer)
    waveguide = gf.path.extrude(path, cross_section)

    c.add_ref(waveguide)

    return c


def _generate_meander_points(
    height: float, padding_length: float, spacing: float, num_turns: int
) -> np.ndarray:
    """
    Generates points for a meander pattern.
    Helper function for meander component.
    """
    step_up_edge = [0, height / 2]
    step_down_edge = [0, -height / 2]
    step_up = [0, height]
    step_down = [0, -height]
    step_horizontal = [spacing, 0]

    steps = (step_down, step_up)
    half_steps = (step_down_edge, step_up_edge)

    turn_points = list(
        chain(*[[steps[i % 2], step_horizontal] for i in range(num_turns)])
    )
    end_step = half_steps[num_turns % 2]

    total_points = (
        [[0, 0], [padding_length, 0], step_up_edge, step_horizontal]
        + turn_points
        + [end_step, [padding_length, 0]]
    )

    return np.array(total_points).cumsum(axis=0)
