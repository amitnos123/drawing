from pydantic import BaseModel
from gdsfactory.typings import LayerSpec
from ..shared import DEFAULT_LAYER, smooth_corners, merge_referenced_shapes
import gdsfactory as gf
import gdsfactory.components as gc
from ..transmon.junctions import RegularJunction
from ..transmon.junctions.base_junction import BaseJunction


class SquidConfig(BaseModel):
    """Configuration for a squid component.
    Attributes:
        flux_hole_width (float): Width of the flux hole.
        flux_hole_length (float): Length of the flux hole.
        outer_length (float): Length of the outer rectangle.
        outer_width (float): Width of the outer rectangle.
        junction_gap_length (float): Length of the gap between junctions.
        layer (LayerSpec): Layer specification for the squid component.
        bridges_layer (LayerSpec | None): Optional layer specification for the bridges over the gap.
    """
    flux_hole_length: float = 15
    flux_hole_width: float = 5
    outer_length: float = 20
    outer_width: float = 10
    junction_gap_length: float = 2
    layer: LayerSpec = DEFAULT_LAYER
    bridges_layer: LayerSpec | None = None

    def build(self) -> gf.Component:
        """
        Builds the squid component by creating the flux hole and junctions.
        Returns:
            gf.Component: The squid component.
        """
        c: gf.Component = gf.Component()

        outer_rectangle = self.create_outer_rectangle(layer = self.layer)
        flux_hole = self.create_flux_hole(layer = self.layer)
        gap_hole_top = self.create_gap_hole(layer = self.layer)
        gap_hole_bottom = self.create_gap_hole(layer = self.layer)

        flux_hole.move((outer_rectangle.center[0] - flux_hole.center[0], outer_rectangle.center[1] - flux_hole.center[1]))
        gap_hole_top.move((outer_rectangle.center[0] - gap_hole_top.center[0], outer_rectangle.ymax - gap_hole_top.ymax))
        gap_hole_bottom.move((outer_rectangle.center[0] - gap_hole_bottom.center[0], outer_rectangle.ymin - gap_hole_bottom.ymin))
        c4 = gf.boolean(outer_rectangle, flux_hole, operation="not", layer=self.layer)
        c4 = gf.boolean(c4, gap_hole_top, operation="not", layer=self.layer)
        c4 = gf.boolean(c4, gap_hole_bottom, operation="not", layer=self.layer)

        c << c4

        if self.bridges_layer != None:
            c << gap_hole_top.remap_layers({self.layer: self.bridges_layer})
            c << gap_hole_bottom.remap_layers({self.layer: self.bridges_layer})

        c.flatten()

        return c

    def create_outer_rectangle(self, layer) -> gf.Component:
        """
        Creates the outer rectangle of the squid.
        Returns:
            gf.Component: The outer rectangle component.
        """
        return self.create_rectangle(length=self.outer_length, width=self.outer_width, layer=layer)

    def create_flux_hole(self, layer) -> gf.Component:
        """
        Creates the flux hole component.
        Returns:
            gf.Component: The flux hole component.
        """
        return self.create_rectangle(length=self.flux_hole_length, width=self.flux_hole_width, layer=layer)
    
    def create_gap_hole(self, layer) -> gf.Component:
        """
        Creates the gap hole component.
        This is the gap between the two junctions in the squid.
        Returns:
            gf.Component: The flux hole component.
        """
        return self.create_rectangle(length=self.junction_gap_length, width=self.junction_gap_width(), layer=layer)

    def create_rectangle(self, length: float = 10, width: float = 1, layer = (1, 0)):
        c = gf.Component()
        c.add_polygon([(0, 0), (length, 0), (length, width), (0, width)], layer=layer)
        return c 

    def junction_gap_width(self) -> float:
        """
        Returns the width of the junction gap.
        """
        return  (self.outer_width - self.flux_hole_width) / 2

    def validate(self) -> None:
        """
        Validates the squid configuration.
        Raises:
            ValueError: If any of the dimensions are not positive or if the outer dimensions are smaller than the flux hole or junction gap.
        Raises:
            ValueError: If the outer dimensions are smaller than the flux hole or junction gap.
        Raises:
            ValueError: If the flux hole dimensions are not positive.
        Raises:
            ValueError: If the outer dimensions are not positive.
        Raises:
            ValueError: If the junction gap length is not positive.
        Raises:
            ValueError: If the outer dimensions are smaller than the flux hole or junction gap.
        """
        if self.flux_hole_width <= 0 or self.flux_hole_length <= 0:
            raise ValueError("Squid flux hole width and length must be positive.")
        if self.outer_length <= 0 or self.outer_width <= 0:
            raise ValueError("Squid outer length and width must be positive.")
        if self.junction_gap_length <= 0:
            raise ValueError("Squid junction gap length must be positive.")
        if self.outer_length < self.flux_hole_length:
            raise ValueError("Squid outer length must be greater than flux hole length.")
        if self.outer_width < self.flux_hole_width:
            raise ValueError("Squid outer width must be greater than flux hole width.")
        if self.outer_length < self.junction_gap_length:
            raise ValueError("Squid outer length must be greater than flux hole length.")
        if self.outer_width < self.junction_gap_width():
            raise ValueError("Squid outer width must be greater than junction gap width.")