"""
Shared utility functions for GDS component creation and manipulation.
Common operations used across different component types.
"""

import gdsfactory as gf
from gdsfactory.typings import LayerSpec
from typing import Tuple

# Type aliases
Coordinate = Tuple[float, float]
Size = Tuple[float, float]

# Constants
DEFAULT_LAYER = (1, 0)
DEFAULT_NUM_POINTS = 300


@gf.cell
def merge_referenced_shapes(component: gf.Component, layer: LayerSpec = DEFAULT_LAYER) -> gf.Component:
    """
    Merges all referenced shapes in a component into a single component.

    Args:
        component: The component containing references to merge.
        layer: Target layer for merged shapes.

    Returns:
        gf.Component: New component with merged geometries.
    """
    merged_component = gf.Component()
    references = list(component.references)

    if not references:
        return component

    # Start with first two references
    merged_result = gf.boolean(
        A=references[0],
        B=references[1],
        operation="or",
        layer=layer,
    )

    # Merge remaining references
    for ref in references[2:]:
        merged_result = gf.boolean(
            A=merged_result,
            B=ref,
            operation="or",
            layer=layer
        )

    # Add merged polygons and ports
    for layer, polygons in merged_result.get_polygons().items():
        for polygon in polygons:
            merged_component.add_polygon(polygon, layer=layer)

    merged_component.add_ports(component.ports)
    return merged_component


@gf.cell
def smooth_corners(
        component: gf.Component,
        radius: float = 1.0,
        num_points: int = DEFAULT_NUM_POINTS,
        layer: LayerSpec = DEFAULT_LAYER
) -> gf.Component:
    """
    Smooths all corners in a component with a given radius.

    Args:
        component: Component to smooth corners.
        radius: Radius for corner rounding in microns.
        num_points: Number of points per full circle for smoothing.
        layer: Target layer for smoothed shapes.

    Returns:
        gf.Component: New component with smoothed corners.
    """
    c = gf.Component()
    radius_db = int(round(radius * 1000))  # Convert to database units

    for _, polygons in component.get_polygons().items():
        for polygon in polygons:
            p_round = polygon.round_corners(radius_db, radius_db, num_points)
            c.add_polygon(p_round, layer=layer)

    c.add_ports(component.ports)
    return c
