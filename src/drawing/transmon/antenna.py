from pydantic import BaseModel
from gdsfactory.typings import LayerSpec
from ..shared import DEFAULT_LAYER, merge_decorator
import gdsfactory.components as gc
import gdsfactory as gf


class AntennaConfig(BaseModel):
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
    length: float = 1400
    width: float = 100
    radius: float = 250
    layer: LayerSpec = DEFAULT_LAYER

    def build(self, c: gf.Component) -> None:
        """
        Integrates the antenna shape into the provided component.

        This method draws the antenna, adds it as a reference to the component,
        and connects the antenna's starting port to the component's antenna port.

        Args:
            c (gf.Component): The component to which the antenna is added.
        """
        antenna = self._draw()
        ref = c << antenna
        ref.connect('start', c.ports["antenna_port"], allow_width_mismatch=True)

    @merge_decorator
    def _draw(self) -> gf.Component:
        """
        Draws the antenna geometry by combining a rectangular and a circular shape.

        Returns:
            gf.Component: A component representing the antenna.
        """
        c = gf.Component()
        compass = gc.compass((self.length, self.width), layer=DEFAULT_LAYER)
        circle = gc.circle(radius=self.radius, layer=DEFAULT_LAYER)

        compass_ref = c << compass
        circle_ref = c << circle

        circle_port = gf.Port(
            name='circle_port',
            center=circle_ref.center,
            layer=DEFAULT_LAYER[0],
            width=self.width,
            orientation=180
        )
        compass_ref.connect("e3", circle_port, allow_type_mismatch=True)
        c.add_port('start', port=compass_ref.ports['e1'])
        return c

