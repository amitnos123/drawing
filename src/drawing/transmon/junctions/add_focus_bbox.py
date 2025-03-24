import gdsfactory as gf
from gdsfactory import Component

from ...shared import DEFAULT_LAYER, JUNCTION_FOCUS_LAYER
import gdsfactory.components as gc

SCALE = 10

def add_focus_bbox(w : Component, right_ref, left_ref, ref_layer = DEFAULT_LAYER,
                   junction_layer = JUNCTION_FOCUS_LAYER):

    union_junction = gf.boolean(left_ref, right_ref, operation='or', layer=ref_layer,
                                layer1=ref_layer, layer2=ref_layer)

    junction_bbox = gc.bbox(union_junction, layer=junction_layer)

    junction_scaled_bbox = w << gc.compass(
        (junction_bbox.size_info.width * SCALE, junction_bbox.size_info.height * SCALE),
        layer=junction_layer)

    junction_scaled_bbox.move(origin=junction_scaled_bbox.center, destination=union_junction.center)