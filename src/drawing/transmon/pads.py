from pydantic import BaseModel
from gdsfactory.typings import LayerSpec
from ..shared import DEFAULT_LAYER, smooth_corners
import gdsfactory as gf
import gdsfactory.components as gc


class PadConfig(BaseModel):
    """
    Configuration for pad components used in the transmon layout.

    Defines the size, corner radius, spacing, and layer for the pads. Also handles
    port placement for electrical connectivity.

    Attributes:
        width (float): Pad width.
        height (float): Pad height.
        radius (float): Corner radius for smoothing (0 for sharp edges).
        distance (float): Horizontal separation between pads.
        layer (LayerSpec): GDS layer specification.
    """
    width: float = 400
    height: float = 1000
    radius: float = 100
    distance: float = 150
    layer: LayerSpec = DEFAULT_LAYER

    def build(self, c: gf.Component) -> tuple:
        """
        Builds pad components and integrates them into the given component.

        The method creates two pads (left and right), applies optional corner rounding,
        and sets up electrical ports.

        Args:
            c (gf.Component): The component into which pads are added.

        Returns:
            tuple: A tuple containing the left and right pad references.
        """
        pad = gc.compass((self.width, self.height), layer=self.layer)
        if self.radius > 0:
            pad = smooth_corners(pad, radius=self.radius, layer=self.layer)

        # Create left and right pads
        left_ref = c << pad
        right_ref = c << pad

        # Position the pads
        right_ref.dmovex(self.distance + self.width)

        # Set ports for the pads
        c.add_port(name="antenna_port", port=right_ref.ports["e3"]) # Port for connecting the antenna
        c.add_port(name="orientation_port", port=left_ref.ports["e1"], port_type='electrical') # Port for orientation
        
        # Return references to the left and right pads
        return left_ref, right_ref

    def validate(self) -> None:
        """
        Validates the pad configuration.

        Raises:
            ValueError: If the pad width or height is non-positive.
            TypeError: If the layer is not of type LayerSpec.
        """
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Pad width and height must be positive.")