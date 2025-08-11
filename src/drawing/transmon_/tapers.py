from pydantic import BaseModel
from gdsfactory.typings import LayerSpec
from ..shared import DEFAULT_LAYER
import gdsfactory.components as gc
import gdsfactory as gf


class TaperConfig(BaseModel):
    """
    Configuration for taper components used to transition between different widths.

    This configuration defines the dimensions of a taper as well as the additional
    extra length for connection components.

    Attributes:
        length (float): Length of the taper.
        wide_width (float): Starting width of the taper.
        narrow_width (float): Ending width of the taper.
        extra_length (float): Additional length for the connection (compass).
        layer (LayerSpec): GDS layer specification.
    """
    length: float = 65
    wide_width: float = 45
    narrow_width: float = 1
    extra_length: float = 5
    layer: LayerSpec = DEFAULT_LAYER

    # single taper
    def _build(self) -> gf.Component:
        """
        Constructs the taper shape by combining a taper and an additional compass.

        Returns:
            gf.Component: A component representing the constructed taper.
        """
        taper = gc.taper(
            length=self.length,
            width1=self.wide_width,
            width2=self.narrow_width,
            port_names=("wide_end", "narrow_end"),
            port_types=("electrical", "electrical"),
            layer=self.layer,
        )

        # gc.compass: Rectangular contact pad with centered ports on rectangle edges (north, south, east, and west)
        # size: Tuple[float, float] rectangle size 
        compass = gc.compass(size=(self.extra_length, self.narrow_width), layer=self.layer)
        
        # Will hold both Taper & Compass
        c = gf.Component()

        # Create taper and compass
        taper_ref = c << taper
        compass_ref = c << compass
        
        # Connect the taper to the compass
        compass_ref.connect('e1', taper_ref.ports['narrow_end'])
        
        # Add ports for connecting to pad and junction
        c.add_port(name='wide_end', port=taper_ref.ports['wide_end'])
        c.add_port(name='narrow_end', port=compass_ref.ports['e3'])
        
        # Taper + Compass connected
        return c

    def build(self, c: gf.Component) -> tuple:
        """
        Adds two taper instances to the provided component.

        This method positions two copies of the taper (left and right) for further integration.

        Args:
            c (gf.Component): The component to which tapers are added.

        Returns:
            tuple: A tuple containing references to the left and right taper components.
        """
        straight_end_taper = self._build()
        
        # Create the tapers
        left_ref = c << straight_end_taper
        right_ref = c << straight_end_taper

        # Return references to the left and right tapers
        return left_ref, right_ref

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