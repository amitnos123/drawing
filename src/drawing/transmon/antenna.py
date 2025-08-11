from ..shared import merge_decorator
import gdsfactory.components as gc
import gdsfactory as gf
from pydantic import computed_field
from pyparsing import cached_property
from ..base_config import BaseConfig
import gdsfactory as gf


class AntennaConfig(BaseConfig):
    """
    Configuration for building an antenna component in a transmon layout.

    This configuration defines the dimensions and layer for the antenna. The antenna
    consists of a rectangular (compass) part and a circular part, which are connected
    to form the final shape.

    Attributes:
        length (float): Length of the rectangular part.
        width (float): Width of the rectangular part.
        radius (float): Radius of the circular part.
        layer (LayerSpec): GDS layer specification for the antenna.
    """
    length: float = 140
    width: float = 10
    radius: float = 25
    
    ANTENNA_START_PORT: str = 'start'

    @computed_field
    @cached_property
    def build(self) -> gf.Component:
        """
        Integrates the antenna shape into the provided component.

        This method draws the antenna, adds it as a reference to the component,
        and connects the antenna's starting port to the component's antenna port.

        Args:
            c (gf.Component): The component to which the antenna is added.
        """
        # Draw the antenna shape
        return self._draw()

    @merge_decorator
    def _draw(self) -> gf.Component:
        """
        Draws the antenna geometry by combining a rectangular and a circular shape.

        Returns:
            gf.Component: A component representing the antenna.
        """
        c = gf.Component()

        # gc.compass: Rectangular contact pad with centered ports on rectangle edges (north, south, east, and west)
        # size: Tuple[float, float] rectangle size 
        compass = gc.compass(size=(self.length, self.width), layer=self.layer)
        circle = gc.circle(radius=self.radius, layer=self.layer)

        # Create compass and circle
        compass_ref = c << compass
        circle_ref = c << circle

        # Create a port for the circle
        circle_port = gf.Port(
            name='circle_port',
            center=circle_ref.center,
            layer=self.layer[0],
            width=self.width,
            orientation=180
        )

        # Connect the circle to the compass
        compass_ref.connect("e3", circle_port, allow_type_mismatch=True)

        # Create the antenna's start port
        c.add_port(self.ANTENNA_START_PORT, port=compass_ref.ports['e1'])

        # return the component with the antenna shape
        return c

    def validate(self) -> None:
        """
        Validates the antenna configuration.

        Raises:
            ValueError: If the antenna length, width, or radius is non-positive.
            TypeError: If the layer is not of type LayerSpec.
        """
        if self.length <= 0 or self.width <= 0 or self.radius <= 0:
            raise ValueError("Antenna dimensions must be positive.")