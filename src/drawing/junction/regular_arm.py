from gdsfactory.typings import LayerSpec
from ..shared import DEFAULT_LAYER
import gdsfactory as gf
import gdsfactory.components as gc
from .base_arm import BaseArmConfig

class RegularArmConfig(BaseArmConfig):
    """
    Configuration for a rectangular arm component.
    Attributes:
        layer (LayerSpec): Layer specification for the regular arm component.
        length (float): Length of the arm.
        width (float): Width of the arm.
    """

    length: float = 10.0
    width: float = 1.0

    def build(self) -> gf.Component:
        c = gf.Component()
        c.add_polygon([(0, 0), (self.length, 0), (self.length, self.width), (0, self.width)], layer=self.layer)
        c.add_port(name="connection", center=(self.length, self.width / 2), width=self.width, orientation=0, layer=self.layer, port_type="electrical")
        c.add_port(name="gap", center=(0, self.width / 2), width=self.width, orientation=180, layer=self.layer, port_type="electrical")
        return c

    def total_length(self) -> float:
        """
        Returns the total length of the arm.
        This method returns the length of the arm.
        """
        return self.length
    
    def validate(self) -> None:
        super().validate()
        if self.length <= 0:
            raise ValueError("Length must be positive.")
        if self.width <= 0:
            raise ValueError("Width must be positive.")