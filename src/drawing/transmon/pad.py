from pydantic import computed_field
from pyparsing import cached_property
from ..base_config import BaseConfig
import gdsfactory as gf
from ..shared import smooth_corners

class PadConfig(BaseConfig):
    """

    Attributes:
        layer (LayerSpec): GDS layer specification.
    """
    width: float = 50
    length: float = 20
    radius: float = 5

    LEFT_CONNECTING_PORT_NAME: str = "left_connection"
    RIGHT_CONNECTING_PORT_NAME: str = "right_connection"

    @computed_field
    @cached_property
    def build(self) -> gf.Component:
        """
        Builds pad components and integrates them into the given component.

        The method creates two pads (left and right), applies optional corner rounding,
        and sets up electrical ports.
        """
        c = gf.Component()
        c.add_polygon([(0, 0), (self.length, 0), (self.length, self.width), (0, self.width)], layer=self.layer)

        c.add_port(name=self.LEFT_CONNECTING_PORT_NAME, center=(0, self.width / 2), width=self.width, orientation=180, layer=self.layer, port_type="electrical")
        c.add_port(name=self.RIGHT_CONNECTING_PORT_NAME, center=(self.length, self.width / 2), width=self.width, orientation=0, layer=self.layer, port_type="electrical")

        if self.radius > 0:
            c = smooth_corners(c, radius=self.radius, layer=self.layer)

        return c

    def validate(self) -> None:
        """
        Validates the pad configuration.

        Raises:
            ValueError: If the pad width or height is non-positive.
            TypeError: If the layer is not of type LayerSpec.
        """
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Pad width and height must be positive.")