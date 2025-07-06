from drawing.transmon.junctions.base_junction import BaseJunction
from typing_extensions import Literal
from ...shared import DEFAULT_LAYER, JUNCTION_FOCUS_LAYER
from gdsfactory.typings import LayerSpec
import gdsfactory as gf
import gdsfactory.components as gc

from .add_focus_bbox import add_focus_bbox


class IrregularJunction(BaseJunction):
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
        # left_taper.connect('wide_end', left_pad.ports['e3'], allow_width_mismatch=True)
        # right_taper.connect('wide_end', right_pad.ports['e1'], allow_width_mismatch=True)
        super().connect_tapers_to_pads(left_pad, right_pad, left_taper, right_taper)
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
        # Calculate the length of each arm
        arm_length = (self.total_length(c) - self.gap) / 2

        # gc.compass: Rectangular contact pad with centered ports on rectangle edges (north, south, east, and west)
        # size: Tuple[float, float] rectangle size 
        right_junction = gc.compass(size=(arm_length, self.width), layer=self.layer)

        # Create L arm shape
        left_junction = self._build_asymmetric_elbow_shape(arm_length)

        # Combining Component
        w = gf.Component()

        # Insert every preview component
        ref = w << c

        # Create left arm
        left_junction = w << left_junction
        
        # Connect left arm toright taper
        left_junction.connect('taper_connection', ref.ports['left_narrow_end'])
        
        # Create port pointing to center of the junction
        w.add_port('left_arm', port=left_junction.ports['inward_connection'])

        # Create right arm
        right_junction = w << right_junction

        # Connect right arm toright taper
        right_junction.connect('e3', ref.ports['right_narrow_end'])

        # Create port pointing to center of the junction
        w.add_port('right_arm', port=right_junction.ports['e1'])

        # Add original ports from preview components
        w.add_ports(c.ports)

        # Adds a bounding box around the junction
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
        # gc.compass: Rectangular contact pad with centered ports on rectangle edges (north, south, east, and west)
        # size: Tuple[float, float] rectangle size 
        horizontal = gc.compass(size=(length, self.width), layer=self.layer)
        vertical = gc.compass(size=(self.thickness, self.vertical_length), layer=self.layer)

        # Combining Component
        c = gf.Component()
        # Combine
        horizontal_ref = c << horizontal
        vertical_ref = c << vertical

        # Connect the horizontal and vertical components
        vertical_ref.connect('e2', horizontal_ref.ports['e4'], allow_width_mismatch=True)
        # Move the vertical component to the correct position
        vertical_ref.move(vertical_ref.size_info.ne, horizontal_ref.size_info.ne)

        # Add ports for connections
        c.add_port('taper_connection', port=horizontal_ref.ports['e1'])
        c.add_port('inward_connection', port=vertical_ref.ports['e4'])

        # return combined component
        return c
