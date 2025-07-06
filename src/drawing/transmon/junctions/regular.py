from drawing.transmon.junctions.base_junction import BaseJunction
from typing_extensions import Literal
from ...shared import DEFAULT_LAYER, JUNCTION_FOCUS_LAYER
from gdsfactory.typings import LayerSpec
import gdsfactory as gf
import gdsfactory.components as gc
from .add_focus_bbox import add_focus_bbox


class RegularJunction(BaseJunction):
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
    junction_focus_layer: LayerSpec = JUNCTION_FOCUS_LAYER

    # def connect_tapers_to_pads(self, left_pad, right_pad, left_taper, right_taper) -> None:
    #     """
    #     Connects tapers to pads for a regular junction.

    #     Args:
    #         left_pad: Left pad component.
    #         right_pad: Right pad component.
    #         left_taper: Taper connecting to the left pad.
    #         right_taper: Taper connecting to the right pad.
    #     """
    #     left_taper.connect('wide_end', left_pad.ports['e3'], allow_width_mismatch=True)
    #     right_taper.connect('wide_end', right_pad.ports['e1'], allow_width_mismatch=True)

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

        w.add_port('junction_left_arm', port=left_ref.ports['e3'])
        w.add_port('junction_right_arm', port=right_ref.ports['e1'])
        w.add_ports(c.ports)

        # adding bbox around the junction at focus function layer
        # using the two parts to make a rect
        add_focus_bbox(w, right_ref, left_ref, ref_layer=self.layer, junction_layer=self.junction_focus_layer)

        return w
