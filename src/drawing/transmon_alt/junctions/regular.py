from pydantic import BaseModel
from typing_extensions import Literal
from ...shared import DEFAULT_LAYER
from gdsfactory.typings import LayerSpec
import gdsfactory as gf
import gdsfactory.components as gc


class RegularJunction(BaseModel):
    """
    Configuration for creating a regular junction between tapers in a transmon layout.

    Attributes:
        type (Literal['regular']): Fixed type for a regular junction.
        width (float): Junction width.
        gap (float): Gap between the connected tapers.
        length (float): Nominal length for the junction.
        layer (LayerSpec): GDS layer specification.
    """
    type: Literal['regular'] = 'regular'
    width: float = 1
    gap: float = 3
    length: float = 10
    layer: LayerSpec = DEFAULT_LAYER

    @staticmethod
    def connect_tapers_to_pads(left_pad, right_pad, left_taper, right_taper) -> None:
        """
        Connects tapers to pads for a regular junction.

        Args:
            left_pad: Left pad component.
            right_pad: Right pad component.
            left_taper: Taper connecting to the left pad.
            right_taper: Taper connecting to the right pad.
        """
        left_taper.connect('wide_end', left_pad.ports['e3'], allow_width_mismatch=True)
        right_taper.connect('wide_end', right_pad.ports['e1'], allow_width_mismatch=True)

    def build(self, c: gf.Component) -> gf.Component:
        """
        Builds the regular junction by placing and connecting junction copies.

        It creates two copies of a junction shape, aligns them to the pre-defined ports, and
        returns a unified component.

        Args:
            c (gf.Component): Component containing existing ports for connection.

        Returns:
            gf.Component: The complete regular junction component.
        """
        left_to_right_distance_x = (c.ports['right_narrow_end'].center[0] -
                                    c.ports['left_narrow_end'].center[0])
        length = (left_to_right_distance_x - self.gap) / 2

        junction = gc.compass((length, self.width), layer=self.layer)
        w = gf.Component()
        ref = w << c
        left_ref = w << junction
        right_ref = w << junction

        left_ref.connect('e1', ref.ports['left_narrow_end'])
        right_ref.connect('e3', ref.ports['right_narrow_end'])

        w.add_port('left_arm', port=left_ref.ports['e3'])
        w.add_port('right_arm', port=right_ref.ports['e1'])
        w.add_ports(c.ports)
        return w
