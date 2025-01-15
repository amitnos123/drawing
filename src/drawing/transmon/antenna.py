import gdsfactory as gf
import gdsfactory.components as gc
from gdsfactory.typings import LayerSpec
# from ..shared import merge_decorator, smooth_corners, DEFAULT_LAYER
from matplotlib import pyplot as plt

from drawing.shared import merge_decorator

DEFAULT_LAYER = (1, 0)


@merge_decorator
def draw_antenna(
        antenna_length: float,
        antenna_width: float,
        antenna_radius: float
):
    c = gf.Component()

    # Create pad with optional corner rounding
    compass = gc.compass((antenna_length, antenna_width), layer=DEFAULT_LAYER)
    circle = gc.circle(radius=antenna_radius, layer=DEFAULT_LAYER)

    compass_ref = c << compass
    circle_ref = c << circle

    circle_port = gf.Port('circle_port', center=circle_ref.center,
                          layer=DEFAULT_LAYER, width=antenna_width, orientation=180)
    compass_ref.connect("e3", circle_port, allow_type_mismatch=True)

    c.add_port('e1', port=compass_ref.ports['e1'])
    return c


if __name__ == '__main__':
    c = draw_antenna(antenna_length=1400,
                     antenna_radius=250,
                     antenna_width=100)

    c.draw_ports()
    c.plot()
    plt.show()
    pass
