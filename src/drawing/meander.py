"""
Meander component implementations for GDS layouts.
Provides different approaches to creating meander patterns.
"""

import gdsfactory as gf
import gdsfactory.components as gc
import numpy as np
from itertools import chain
from gdsfactory.typings import LayerSpec
from shared_utilities import DEFAULT_LAYER


@gf.cell
def meander_euler(
        wire_width: float = 0.2,
        height: float = 10,
        padding_length: float = 3,
        spacing: float = 3,
        num_turns: int = 9,
        radius: float = 1,
        layer: LayerSpec = DEFAULT_LAYER
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
        num_turns=num_turns
    )

    path = gf.path.smooth(
        points,
        radius=radius,
        bend=gf.path.euler,
        use_eff=True,
        npoints=320,
        p=1
    )

    cross_section = gf.cross_section.strip(width=wire_width, layer=layer)
    waveguide = gf.path.extrude(path, cross_section)
    c.add_ref(waveguide)

    return c


def _generate_meander_points(
        height: float,
        padding_length: float,
        spacing: float,
        num_turns: int
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

    turn_points = list(chain(*[[steps[i % 2], step_horizontal] for i in range(num_turns)]))
    end_step = half_steps[num_turns % 2]

    total_points = ([[0, 0], [padding_length, 0], step_up_edge, step_horizontal] +
                    turn_points +
                    [end_step, [padding_length, 0]])

    return np.array(total_points).cumsum(axis=0)


@gf.cell
def meander_optimal_turn(wire_width: float = 0.2,
                         height: float = 10,
                         padding_length: float = 3,
                         spacing: float = 2,
                         num_turns: int = 9
                         ):
    turn = gc.optimal_90deg(width=wire_width)

    turn_size = turn.xmax - turn.xmin

    padding_compass = gc.compass(size=(padding_length, wire_width))
    spacing_compass = gc.compass(size=(spacing, wire_width))
    height_compass = gc.compass(size=(height - 2 * turn_size, wire_width))
    padding_height_compass = gc.compass(size=(height / 2 - 2 * turn_size, wire_width))

    c = gf.Component()

    start_wg = c << padding_compass

    prev_port = start_wg.ports['e3']

    # going up
    ref = c << turn
    ref.connect('e1', prev_port, allow_type_mismatch=True)
    prev_port = ref.ports['e2']

    # padding height compass for start
    ref = c << padding_height_compass
    ref.connect('e1', prev_port, allow_type_mismatch=True)
    prev_port = ref.ports['e3']

    turn_ports_naming = [('e2', 'e1'), ('e1', 'e2')]

    for i in range(num_turns):

        turn_connect_name, turn_prev_name = turn_ports_naming[i % 2]

        prev_port = _optimal_full_turn_with_spacing(c, turn, spacing_compass,
                                                    turn_connect_name,
                                                    turn_prev_name,
                                                    prev_port)

        # if last then use half hieght_compass
        if i == num_turns - 1:
            vertical_compass = padding_height_compass
        else:
            vertical_compass = height_compass

        ref = c << vertical_compass
        ref.connect('e1', prev_port, allow_type_mismatch=True)
        prev_port = ref.ports['e3']

    ref = c << turn
    turn_connect_name, turn_prev_name = turn_ports_naming[num_turns % 2]
    ref.connect(turn_connect_name, prev_port, allow_type_mismatch=True)
    prev_port = ref.ports[turn_prev_name]

    end_wg = c << padding_compass
    end_wg.connect('e1', prev_port, allow_type_mismatch=True)

    c.add_port('e1', start_wg.ports['e1'])
    c.add_port('e2', end_wg.ports['e3'])

    return c


def _optimal_full_turn_with_spacing(component, optimal_turn, spacing_compass,
                                    turn_connect_name, turn_prev_name,
                                    prev_port):
    c = component
    ref = c << optimal_turn
    ref.connect(turn_connect_name, prev_port, allow_type_mismatch=True)
    prev_port = ref.ports[turn_prev_name]

    ref = c << spacing_compass
    ref.connect('e1', prev_port, allow_type_mismatch=True)
    prev_port = ref.ports['e3']

    ref = c << optimal_turn
    ref.connect(turn_connect_name, prev_port, allow_type_mismatch=True)
    prev_port = ref.ports[turn_prev_name]

    return prev_port
