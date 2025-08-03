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

    def build(self, c: gf.Component, leftPortName = 'left_narrow_end', rightPortName = 'right_narrow_end', focus_box = True) -> gf.Component:
        """
        Builds the regular junction by placing and connecting junction copies.

        It creates two copies of a junction shape, aligns them to the pre-defined ports, and
        returns a unified component.

        Args:
            c (gf.Component): Component containing existing ports for connection.

        Returns:
            gf.Component: The complete regular junction component.
        """
        # Calculate the length of each arm
        arm_length = (self.total_length(c, leftPortName=leftPortName, rightPortName=rightPortName) - self.gap) / 2

        # gc.compass: Rectangular contact pad with centered ports on rectangle edges (north, south, east, and west)
        # size: Tuple[float, float] rectangle size 
        junction = gc.compass((arm_length, self.width), layer=self.layer)

        # Combining Component
        w = gf.Component()

        # Insert every preview component
        ref = w << c
        # Create arms
        left_ref = w << junction
        right_ref = w << junction

        # Connect arms to their respective tapers
        if leftPortName in ref.ports and rightPortName in ref.ports:
            self.conntect_to_tapers(left_ref, right_ref, ref.ports[leftPortName], ref.ports[rightPortName])
        else:
            left_ref.dmovex(-(arm_length + self.gap) / 2)
            right_ref.dmovex((arm_length + self.gap) / 2)

        # Add ports to arm
        w.add_port('junction_left_arm', port=left_ref.ports['e3'])
        w.add_port('junction_right_arm', port=right_ref.ports['e1'])
        w.add_ports(c.ports)

        if focus_box:
            # Adds a bounding box around the junction
            add_focus_bbox(w, right_ref, left_ref, ref_layer=self.layer, junction_layer=self.junction_focus_layer)

        # Return combined component
        return w
