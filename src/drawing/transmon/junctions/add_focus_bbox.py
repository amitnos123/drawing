import gdsfactory as gf
from gdsfactory import Component

from ...shared import DEFAULT_LAYER, JUNCTION_FOCUS_LAYER
import gdsfactory.components as gc

SCALE = 10

def add_focus_bbox(w : Component, right_ref, left_ref, ref_layer = DEFAULT_LAYER,
                   junction_layer = JUNCTION_FOCUS_LAYER):
    """    Adds a bounding box around the junction.
    Args:
        w (Component): The component to which the bounding box will be added.
        right_ref: Reference to the right arm of the junction.
        left_ref: Reference to the left arm of the junction.
        ref_layer (LayerSpec): Layer specification for the references.
        junction_layer (LayerSpec): Layer specification for the junction bounding box.
    """

    # Component which is a union of the left and right arms of the junction
    union_junction = gf.boolean(left_ref, right_ref, operation='or', layer=ref_layer,
                                layer1=ref_layer, layer2=ref_layer)

    # Create a bounding box (bbox) around the union junction
    junction_bbox = gc.bbox(union_junction, layer=junction_layer)

    # Scale the bounding box size by a factor of SCALE
    junction_scaled_bbox = w << gc.compass(
        (junction_bbox.size_info.width * SCALE, junction_bbox.size_info.height * SCALE),
        layer=junction_layer)

    # Move the scaled bounding box to the center of the union junction
    junction_scaled_bbox.move(origin=junction_scaled_bbox.center, destination=union_junction.center)