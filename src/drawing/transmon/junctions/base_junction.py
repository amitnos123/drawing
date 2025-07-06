from pydantic import BaseModel
from typing_extensions import Literal
from ...shared import DEFAULT_LAYER, JUNCTION_FOCUS_LAYER
from gdsfactory.typings import LayerSpec
import gdsfactory as gf
import gdsfactory.components as gc
from .add_focus_bbox import add_focus_bbox


class BaseJunction(BaseModel):
    """
    Virtual Class for creating junction classes between tapers in a transmon layout.

    Attributes:
        layer (LayerSpec): GDS layer specification.
    """
    layer: LayerSpec = DEFAULT_LAYER
    junction_focus_layer: LayerSpec = JUNCTION_FOCUS_LAYER

    def connect_tapers_to_pads(self, left_pad, right_pad, left_taper, right_taper) -> None:
        """
        Connects tapers to pads for a regular junction.

        Args:
            left_pad: Left pad component.
            right_pad: Right pad component.
            left_taper: Taper connecting to the left pad.
            right_taper: Taper connecting to the right pad.
        """
        # Connect the wide ends of the tapers to the respective pads
        left_taper.connect('wide_end', left_pad.ports['e3'], allow_width_mismatch=True)
        right_taper.connect('wide_end', right_pad.ports['e1'], allow_width_mismatch=True)

    def build(self, c: gf.Component) -> gf.Component:
        raise NameError("Junction build method is not defined.") # "BaseJunction is a virtual class and should not be instantiated directly."

    def validate(self) -> None:
        """
        Validates the junction configuration.

        Raises:
            ValueError: If the layer is not set.
        """
        if not self.layer:
            raise ValueError("Layer must be specified for the junction.")