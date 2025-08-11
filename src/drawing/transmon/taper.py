from pydantic import computed_field
from pyparsing import cached_property
from ..base_config import BaseConfig
import gdsfactory as gf


class TaperConfig(BaseConfig):
    """
    """
    length: float = 10
    wide_width: float = 5
    narrow_width: float = 1

    WIDE_CONNECTING_PORT_NAME: str = "wide_connection"
    NARROW_CONNECTING_PORT_NAME: str = "narrow_connection"

    @computed_field
    @cached_property
    def build(self) -> gf.Component:
        c = gf.Component()

        c.add_polygon([(0,self.wide_width/2), (self.length, self.narrow_width/2), (self.length, -self.narrow_width/2), (0,-self.wide_width/2)], layer=self.layer)
        
        # Add ports for connecting to pad and junction
        c.add_port(name=self.WIDE_CONNECTING_PORT_NAME, center=(0, 0), width=self.wide_width, orientation=180, layer=self.layer, port_type="electrical")
        c.add_port(name=self.NARROW_CONNECTING_PORT_NAME, center=(self.length, 0), width=self.narrow_width, orientation=0, layer=self.layer, port_type="electrical")
        
        # Taper + Compass connected
        return c

    def validate(self):
        """
        Validates the taper configuration.

        This method checks if the configuration parameters are valid.
        """
        if self.length <= 0 or self.wide_width <= 0 or self.narrow_width <= 0:
            raise ValueError(
                "Taper length and widths must be positive values."
            )
        if self.wide_width < self.narrow_width:
            raise ValueError(
                "Wide width must be greater than or equal to narrow width."
            )