from pydantic import BaseModel
from typing_extensions import Literal
from ...shared import DEFAULT_LAYER, JUNCTION_FOCUS_LAYER
from gdsfactory.typings import LayerSpec
import gdsfactory as gf
import gdsfactory.components as gc

from .add_focus_bbox import add_focus_bbox


class IrregularJunction(BaseModel):
    """
    Configuration for creating an irregular junction between tapers in a transmon layout.

    Attributes:
        type (Literal['irregular']): Fixed type for the irregular junction.
        width (float): Width of the junction.
        thickness (float): Thickness parameter for the asymmetric elbow shape.
        vertical_length (float): Vertical length for the elbow shape.
        gap (float): Gap between junction components.
        layer (LayerSpec): GDS layer specification.
    """
    type: Literal['irregular'] = 'irregular'
    width: float = 1
    thickness: float = 2
    vertical_length: float = 6
    gap: float = 3
    layer: LayerSpec = DEFAULT_LAYER
    junction_focus_layer: LayerSpec = JUNCTION_FOCUS_LAYER

    def connect_tapers_to_pads(self, left_pad, right_pad, left_taper, right_taper) -> None:
        """
        Connects tapers to their respective pads.

        Args:
            left_pad: Left pad component.
            right_pad: Right pad component.
            left_taper: Taper connecting to the left pad.
            right_taper: Taper connecting to the right pad.
        """
        left_taper.connect('wide_end', left_pad.ports['e3'], allow_width_mismatch=True)
        right_taper.connect('wide_end', right_pad.ports['e1'], allow_width_mismatch=True)
        right_taper.dmovey(-self.vertical_length / 2)

    def build(self, c: gf.Component) -> gf.Component:
        """
        Constructs the irregular junction by connecting pads and tapers.

        It calculates distances, builds both left and right junction components, and connects
        them to create a unified junction.

        Args:
            c (gf.Component): The main component containing pre-placed ports.

        Returns:
            gf.Component: A component representing the complete irregular junction.
        """
        left_to_right_distance_x = (c.ports['right_narrow_end'].center[0] -
                                    c.ports['left_narrow_end'].center[0])
        length = (left_to_right_distance_x - self.gap) / 2

        right_junction = gc.compass((length, self.width), layer=self.layer)
        left_junction = self._build_asymmetric_elbow_shape(length)

        w = gf.Component()
        ref = w << c
        left_junction = w << left_junction
        left_junction.connect('taper_connection', ref.ports['left_narrow_end'])
        w.add_port('left_arm', port=left_junction.ports['inward_connection'])

        right_junction = w << right_junction
        right_junction.connect('e3', ref.ports['right_narrow_end'])
        w.add_port('right_arm', port=right_junction.ports['e1'])

        add_focus_bbox(w, right_junction, left_junction, ref_layer=self.layer, junction_layer=self.junction_focus_layer)

        return w

    def _build_asymmetric_elbow_shape(self, length: float) -> gf.Component:
        """
        Constructs an asymmetric elbow shape used in the junction.

        Combines a horizontal and a vertical component to create a non-symmetric elbow.

        Args:
            length (float): Length for the horizontal part.

        Returns:
            gf.Component: The asymmetric elbow component.
        """
        horizontal = gc.compass((length, self.width), layer=self.layer)
        vertical = gc.compass((self.thickness, self.vertical_length), layer=self.layer)

        c = gf.Component()
        horizontal_ref = c << horizontal
        vertical_ref = c << vertical

        vertical_ref.connect('e2', horizontal_ref.ports['e4'], allow_width_mismatch=True)
        vertical_ref.move(vertical_ref.size_info.ne, horizontal_ref.size_info.ne)

        c.add_port('taper_connection', port=horizontal_ref.ports['e1'])
        c.add_port('inward_connection', port=vertical_ref.ports['e4'])
        return c
