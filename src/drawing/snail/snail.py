from pydantic import BaseModel
from gdsfactory.typings import LayerSpec
from ..shared import DEFAULT_LAYER, smooth_corners
import gdsfactory as gf
import gdsfactory.components as gc


class SnailConfig(BaseModel):
    """
    """
    width: float = 400
    height: float = 1000
    radius: float = 100
    distance: float = 150
    layer: LayerSpec = DEFAULT_LAYER

    def build(self) -> gf.Component:
        """
        """
        c = gf.Component()
        return c

    def validate(self) -> None:
        """
        """
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Snail width and height must be positive.")