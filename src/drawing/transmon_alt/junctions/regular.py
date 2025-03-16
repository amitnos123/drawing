from pydantic import BaseModel
from typing_extensions import Literal
from ...shared import DEFAULT_LAYER
from gdsfactory.typings import LayerSpec
import gdsfactory as gf
import gdsfactory.components as gc


class RegularJunction(BaseModel):
    type: Literal['regular'] = 'regular'
    width: float = 1
    gap: float = 3
    length: float = 10
    layer: LayerSpec = DEFAULT_LAYER

    @staticmethod
    def connect_tapers_to_pads(left_pad, right_pad, left_taper, right_taper):
        left_taper.connect('wide_end', left_pad.ports['e3'], allow_width_mismatch=True)
        right_taper.connect('wide_end', right_pad.ports['e1'], allow_width_mismatch=True)


    def build(self, c):

        # check the distance between the end of the tapers
        left_to_right_distance_x = (c.ports['right_narrow_end'].center[0] - c.ports['left_narrow_end'].center[0]) / 1000
        left_to_right_distance_y = (c.ports['right_narrow_end'].center[1] - c.ports['left_narrow_end'].center[1]) / 1000

        length = (left_to_right_distance_x - self.gap) / 2

        junction = gc.compass((length, self.width), layer=self.layer)

        w = gf.Component()
        ref = w << c
        left_ref = w << junction
        right_ref = w << junction
        # left component

        left_ref.connect('e1', ref.ports['left_narrow_end'])
        right_ref.connect('e3', ref.ports['right_narrow_end'])

        w.add_port('left_arm', left_ref.ports['e3'])
        w.add_port('right_arm', right_ref.ports['e1'])

        w.add_ports(c.ports)

        return w

        # w = gf.Component()
        # ref = w << junction

        # left component
        # w.add_port('taper_connection', ref.ports['e4'])
        # w.add_port('inward_connection', ref.ports['e2'])



    def integrate(self, left_pad, right_pad, left_taper, right_taper):
        pass


