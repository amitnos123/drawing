from pydantic import BaseModel
from typing_extensions import Literal
from ...shared import DEFAULT_LAYER
from gdsfactory.typings import LayerSpec
import gdsfactory as gf
import gdsfactory.components as gc



# DEFAULT_LAYER = (1, 0)

class IrregularJunction(BaseModel):
    type: Literal['irregular'] = 'irregular'
    width: float = 1
    thickness: float = 2
    vertical_length: float = 6
    gap: float = 3
    # length: float = 10
    layer: LayerSpec = DEFAULT_LAYER

    def connect_tapers_to_pads(self, left_pad, right_pad, left_taper, right_taper):
        left_taper.connect('wide_end', left_pad.ports['e3'], allow_width_mismatch=True)
        right_taper.connect('wide_end', right_pad.ports['e1'], allow_width_mismatch=True)
        right_taper.dmovey(-self.vertical_length / 2)

    def build(self, c):

        left_to_right_distance_x = (c.ports['right_narrow_end'].center[0] - c.ports['left_narrow_end'].center[0]) / 1000
        left_to_right_distance_y = (c.ports['right_narrow_end'].center[1] - c.ports['left_narrow_end'].center[1]) / 1000

        length = (left_to_right_distance_x - self.gap) / 2


        right_junction = gc.compass((length, self.width), layer=self.layer)
        left_junction = self._build_asymmetric_elbow_shape(length)


        # c = gf.Component()
        w = gf.Component()
        ref = w << c
        left_junction = w << left_junction

        left_junction.connect('taper_connection', ref.ports['left_narrow_end'])
        w.add_port('left_arm', left_junction.ports['inward_connection'])

        # left component

        right_junction = w << right_junction
        right_junction.connect('e3', ref.ports['right_narrow_end'])

        # right component
        w.add_port('right_arm', right_junction.ports['e1'])

        return w

        # return {'left': c, 'right': w}


    def _build_asymmetric_elbow_shape(self, length):
        horizontal = gc.compass((length, self.width), layer=self.layer)
        vertical = gc.compass((self.thickness, self.vertical_length), layer=self.layer)

        c = gf.Component()
        horizontal_ref = c << horizontal
        vertical_ref = c << vertical

        vertical_ref.connect('e2', horizontal_ref.ports['e4'], allow_width_mismatch=True)
        vertical_ref.move(vertical_ref.size_info.ne, horizontal_ref.size_info.ne)

        c.add_port('taper_connection', horizontal_ref.ports['e1'])
        c.add_port('inward_connection', vertical_ref.ports['e4'])

        return c

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    constructor = IrregularJunction()
    b = constructor.build()
    c = b['left']
    c.draw_ports()
    c.plot()
    plt.show()






