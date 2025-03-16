from pydantic import BaseModel
from gdsfactory.typings import LayerSpec
from ..shared import DEFAULT_LAYER, merge_decorator
import gdsfactory.components as gc
import gdsfactory as gf


class AntennaConfig(BaseModel):
    length: float = 1400
    width: float = 100
    radius: float = 250
    layer: LayerSpec = DEFAULT_LAYER

    def build(self, c):
        # Create rectangular part of the antenna
        antenna = self._draw()

        ref = c << antenna

        # Connect the circle to the rectangle
        ref.connect('start', c.ports["antenna_port"], allow_width_mismatch=True)


    @merge_decorator
    def _draw(self):
        c = gf.Component()

        # Create pad with optional corner rounding
        compass = gc.compass((self.length, self.width), layer=DEFAULT_LAYER)
        circle = gc.circle(radius=self.radius, layer=DEFAULT_LAYER)

        compass_ref = c << compass
        circle_ref = c << circle

        circle_port = gf.Port('circle_port', center=circle_ref.center,
                              layer=DEFAULT_LAYER, width=self.width, orientation=180)
        compass_ref.connect("e3", circle_port, allow_type_mismatch=True)

        c.add_port('start', port=compass_ref.ports['e1'])
        return c
