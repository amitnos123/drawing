import gdsfactory as gf
import shapely
import numpy as np
from .config import ExportConfig

from shapely.geometry import Point
from shapely.ops import nearest_points


def find_new_port_location(original_port, simplified_polygon):
    """
    Finds the new location of a port after polygon simplification.

    Args:
        original_port (tuple): Coordinates of the original port as (x, y).
        simplified_polygon (shapely.geometry.Polygon): Simplified polygon.

    Returns:
        tuple: Coordinates of the new port location on the simplified polygon.
    """
    # Create a Point object for the original port
    port_point = Point(original_port)

    # Find the nearest point on the simplified polygon
    nearest_point_on_polygon = nearest_points(port_point, simplified_polygon)[1]

    # Return the coordinates of the nearest point
    return nearest_point_on_polygon.x, nearest_point_on_polygon.y


def parse_component(component: gf.Component, config: ExportConfig):
    ports = component.ports
    ports_to_center = dict(map(lambda x: (x.name, x.dcenter), ports))

    hfss_variables = {}

    points = component.get_polygons_points()[1][0].tolist()

    if config.tolerance > 0:
        simplified = shapely.simplify(
            shapely.Polygon(points), tolerance=config.tolerance
        )
        points = list(simplified.exterior.coords)

        ports_to_center = dict(
            map(
                lambda x: (x[0], find_new_port_location(x[1], simplified)),
                ports_to_center.items(),
            )
        )

    if config.align_by == "port":
        center = ports_to_center.pop(config.port)
        align_by_port_var_name = config.port
        align_by_point = center
    elif config.align_by == "xmin":
        align_by_point = min(points, key=lambda x: x[0])
        align_by_port_var_name = "offset"
    else:
        raise ValueError(f"Unidentified value for align by: {config.align_by=}")

    points = np.array(points)
    points -= align_by_point

    # get offset value
    name = config.name
    unit = config.unit

    # adding all the ports to the hfss variables
    for k, v in ports_to_center.items():
        hfss_variables[k] = (v[0] - align_by_point[0], v[1] - align_by_point[1])

    # converting hfss_variables to x direction and y direction
    dependent_variables = {}
    for k, v in hfss_variables.items():
        dependent_variables[f"{name}_{k}_x"] = (
            f"{name}_{align_by_port_var_name}_x + {v[0]}{unit}"
        )
        dependent_variables[f"{name}_{k}_y"] = (
            f"{name}_{align_by_port_var_name}_y + {v[1]}{unit}"
        )

    # adding the reference variable
    independent_variables = {
        f"{name}_{align_by_port_var_name}_x": f"0{unit}",
        f"{name}_{align_by_port_var_name}_y": f"0{unit}"
    }

    points_as_string = [
        (
            f"{name}_{align_by_port_var_name}_x + {x}um",
            f"{name}_{align_by_port_var_name}_y + {y}um",
            "0um",
        )
        for x, y in points
    ]

    return points_as_string, independent_variables, dependent_variables
