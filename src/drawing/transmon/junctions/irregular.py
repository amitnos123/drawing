from pydantic import BaseModel
from typing_extensions import Literal
# from ...shared import DEFAULT_LAYER
from gdsfactory.typings import LayerSpec
import gdsfactory as gf
import gdsfactory.components as gc



DEFAULT_LAYER = (1, 0)

class IrregularJunction(BaseModel):
    type: Literal['irregular'] = 'irregular'
    width: float = 1
    junction_thickness: float = 2
    junction_vertical_length: float = 4
    gap: float = 3
    length: float = 10
    layer: LayerSpec = DEFAULT_LAYER

    def build(self):

        right_junction = gc.compass((self.width, self.length), layer=self.layer)
        left_junction = self._build_asymmetric_elbow_shape()


        c = gf.Component()
        ref = c << left_junction

        # left component
        c.add_port('taper_connection', port=ref.ports['taper_connection'])
        c.add_port('inward_connection', port=ref.ports['inward_connection'])

        w = gf.Component()
        ref = w << right_junction

        # right component
        w.add_port('taper_connection', port=ref.ports['e4'])
        w.add_port('inward_connection', port=ref.ports['e2'])

        return {'left': c, 'right': w}


    def _build_asymmetric_elbow_shape(self):
        horizontal = gc.compass((self.width, self.length), layer=self.layer)
        vertical = gc.compass((self.junction_thickness, self.junction_vertical_length), layer=self.layer)

        c = gf.Component()
        horizontal_ref = c << horizontal
        vertical_ref = c << vertical

        vertical_ref.connect('e2', horizontal_ref.ports['e1'], allow_width_mismatch=True)
        vertical_ref.move(vertical_ref.size_info.se, horizontal_ref.size_info.se)

        c.add_port('taper_connection', port=horizontal_ref.ports['e2'])
        c.add_port('inward_connection', port=vertical_ref.ports['e4'])

        return c

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    constructor = IrregularJunction()
    b = constructor.build()
    c = b['left']
    c.draw_ports()
    c.plot()
    plt.show()






