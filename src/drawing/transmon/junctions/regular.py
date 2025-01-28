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

    def build(self):
        junction = gc.compass((self.width, self.length), layer=self.layer)

        c = gf.Component()
        ref = c << junction

        # left component
        c.add_port('taper_connection', ref.ports['e2'])
        c.add_port('inward_connection', ref.ports['e4'])

        w = gf.Component()
        ref = w << junction

        # left component
        w.add_port('taper_connection', ref.ports['e4'])
        w.add_port('inward_connection', ref.ports['e2'])

        return {'left': c, 'right': w}


