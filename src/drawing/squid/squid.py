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
        top_junction (BaseJunction): Junction at the top of the squid.
        bottom_junction (BaseJunction): Junction at the bottom of the squid.
        layer (LayerSpec): Layer specification for the squid component.
    """
    flux_hole_width: float = 1
    flux_hole_length: float = 5
    top_junction: BaseJunction = RegularJunction()
    bottom_junction: BaseJunction = RegularJunction()
    layer: LayerSpec = DEFAULT_LAYER

    def build(self) -> gf.Component:
        """
        Builds a squid component with a flux hole and two junctions.
        Returns:
            gf.Component: The squid component.
        """
        c: gf.Component = gf.Component()
        # tjc = top junction component
        tjc: gf.Component = self.top_junction.build(gf.Component(), focus_box=False)
        # bjc = bottom junction component
        bjc: gf.Component = self.bottom_junction.build(gf.Component(), focus_box=False)
        
        tjc_ref = c << tjc
        bjc_ref = c << bjc

        tjc_ref.movey((self.flux_hole_width / 2 + self.top_junction.width))
        bjc_ref.movey(-(self.flux_hole_width / 2 + self.bottom_junction.width))

        rectangle_length = (self.top_junction.total_length(c=c) - self.flux_hole_length) / 2
        rectangle_width = tjc_ref.ymax - bjc_ref.ymin
        r_right = self.straight(
            length = rectangle_length, 
            width = rectangle_width,
            layer = self.layer
        )

        r_left = self.straight(
            length = rectangle_length, 
            width = rectangle_width,
            layer = self.layer
        )
        
        
        r_right_ref = c << r_right
        r_left_ref = c << r_left

        r_right_ref.movex(tjc_ref.xmax - r_right_ref.xmin)
        r_right_ref.movey(tjc_ref.ymax - r_right_ref.ymax)

        r_left_ref.movex(tjc_ref.xmin - r_left_ref.xmax)
        r_left_ref.movey(tjc_ref.ymax - r_left_ref.ymax)

        c.flatten()

        return c

    def straight(self, length: float = 10, width: float = 1, layer = (1, 0)):
        c = gf.Component()
        c.add_polygon([(0, 0), (length, 0), (length, width), (0, width)], layer=layer)
        return c 

    def validate(self) -> None:
        """
        """
        if self.flux_hole_width <= 0 or self.flux_hole_length <= 0:
            raise ValueError("Squid flux hole width and length must be positive.")
        if not isinstance(self.top_junction, RegularJunction):
            raise TypeError("Only RegularJunction is supported for top junction.")
        if not isinstance(self.bottom_junction, RegularJunction):
            raise TypeError("Only RegularJunction is supported for top junction.")
        
        top_junction_total_length = self.top_junction.total_length(c=gf.Component())
        bottom_junction_total_length = self.bottom_junction.total_length(c=gf.Component())
        if top_junction_total_length != bottom_junction_total_length:
            raise ValueError("Only support for junctions with the same total length.")
        if top_junction_total_length <= self.flux_hole_length:
            raise ValueError("Junction length must be greater than flux hole length.")

        self.top_junction.validate()
        self.bottom_junction.validate()