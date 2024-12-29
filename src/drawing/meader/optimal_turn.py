import gdsfactory as gf
import gdsfactory.components as gc
from ..shared import merge_decorator


@merge_decorator
@gf.cell
def meander_optimal_turn(
    wire_width: float = 0.2,
    height: float = 10,
    padding_length: float = 3,
    spacing: float = 2,
    num_turns: int = 9,
):
    turn = gc.optimal_90deg(width=wire_width)

    turn_size = turn.xmax - turn.xmin

    padding_compass = gc.compass(size=(padding_length, wire_width))
    spacing_compass = gc.compass(size=(spacing, wire_width))
    height_compass = gc.compass(size=(height - 2 * turn_size, wire_width))
    padding_height_compass = gc.compass(size=(height / 2 - 2 * turn_size, wire_width))

    c = gf.Component()

    start_wg = c << padding_compass

    prev_port = start_wg.ports["e3"]

    # going up
    ref = c << turn
    ref.connect("e1", prev_port, allow_type_mismatch=True)
    prev_port = ref.ports["e2"]

    # padding height compass for start
    ref = c << padding_height_compass
    ref.connect("e1", prev_port, allow_type_mismatch=True)
    prev_port = ref.ports["e3"]

    turn_ports_naming = [("e2", "e1"), ("e1", "e2")]

    for i in range(num_turns):
        turn_connect_name, turn_prev_name = turn_ports_naming[i % 2]

        prev_port = _optimal_full_turn_with_spacing(
            c, turn, spacing_compass, turn_connect_name, turn_prev_name, prev_port
        )

        # if last then use half hieght_compass
        if i == num_turns - 1:
            vertical_compass = padding_height_compass
        else:
            vertical_compass = height_compass

        ref = c << vertical_compass
        ref.connect("e1", prev_port, allow_type_mismatch=True)
        prev_port = ref.ports["e3"]

    ref = c << turn
    turn_connect_name, turn_prev_name = turn_ports_naming[num_turns % 2]
    ref.connect(turn_connect_name, prev_port, allow_type_mismatch=True)
    prev_port = ref.ports[turn_prev_name]

    end_wg = c << padding_compass
    end_wg.connect("e1", prev_port, allow_type_mismatch=True)

    c.add_port("e1", start_wg.ports["e1"])
    c.add_port("e2", end_wg.ports["e3"])

    return c


def _optimal_full_turn_with_spacing(
    component,
    optimal_turn,
    spacing_compass,
    turn_connect_name,
    turn_prev_name,
    prev_port,
):
    c = component
    ref = c << optimal_turn
    ref.connect(turn_connect_name, prev_port, allow_type_mismatch=True)
    prev_port = ref.ports[turn_prev_name]

    ref = c << spacing_compass
    ref.connect("e1", prev_port, allow_type_mismatch=True)
    prev_port = ref.ports["e3"]

    ref = c << optimal_turn
    ref.connect(turn_connect_name, prev_port, allow_type_mismatch=True)
    prev_port = ref.ports[turn_prev_name]

    return prev_port
