from pydantic import BaseModel
from gdsfactory.typings import LayerSpec
from ..shared import DEFAULT_LAYER
import gdsfactory.components as gc
import gdsfactory as gf


class TaperConfig(BaseModel):
    length: float = 65
    wide_width: float = 45
    narrow_width: float = 1
    extra_length: float = 5
    layer: LayerSpec = DEFAULT_LAYER

    def _build(self):
        taper = gc.taper(
            length=self.length,
            width1=self.wide_width,
            width2=self.narrow_width,
            port_names=("wide_end", "narrow_end"),
            port_types=("electrical", "electrical"),
            layer=self.layer,
        )

        compass = gc.compass((self.extra_length, self.narrow_width), layer=self.layer)

        c = gf.Component()

        taper_ref = c << taper
        compass_ref = c << compass
        compass_ref.connect('e1', taper_ref.ports['narrow_end'])

        c.add_port('wide_end', taper_ref.ports['wide_end'])
        c.add_port('narrow_end', compass_ref.ports['e3'])

        return c


    def build(self, c):
        straight_end_taper = self._build()

        # c = gf.Component()
        left_ref = c << straight_end_taper
        right_ref = c << straight_end_taper

        # Add ports for connectivity
        # c.add_port("wide_end", ref.ports["wide_end"])
        # c.add_port("narrow_end", ref.ports["narrow_end"])

        return left_ref, right_ref
