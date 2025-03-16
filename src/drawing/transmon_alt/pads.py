from pydantic import BaseModel
from gdsfactory.typings import LayerSpec
from ..shared import DEFAULT_LAYER, smooth_corners
import gdsfactory as gf
import gdsfactory.components as gc


class PadConfig(BaseModel):
    width: float = 400
    height: float = 1000
    radius: float = 100 # 0 means sharp edges
    distance: float = 150
    layer: LayerSpec = DEFAULT_LAYER

    def build(self, c):
        pad = gc.compass((self.width, self.height), layer=self.layer)
        if self.radius > 0:
            pad = smooth_corners(pad, radius=self.radius, layer=self.layer)

        # Add ports for connectivity
        # c = gf.Component()
        left_ref = c << pad
        right_ref = c << pad
        right_ref.dmovex(self.distance + self.width)

        # c.add_port("right_connection", right_ref.ports["e1"])
        c.add_port("antenna_port", right_ref.ports["e3"])
        c.add_port("orientation_port", left_ref.ports["e1"], port_type='electrical')

        return left_ref, right_ref
