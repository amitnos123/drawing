from typing import Literal
import gdsfactory as gf
import shapely
import numpy as np
from .config import ExportConfig

from shapely.geometry import Point
from shapely.ops import nearest_points
from numpy.typing import NDArray


def construct_rotation(origin: NDArray, target: NDArray):
    # origin = np.array([np.cos(origin_orientation_deg)]) * np.array([1, 0, 0])
    v = np.cross(origin, target)
    cosine_theta = np.dot(origin, target)  # 1 -cos(theta) / sin^2

    # Skew-symmetric matrix of v
    v_cross = np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0]
    ])

    # angle rotation
    c = (1 - cosine_theta) / np.dot(v, v)

    # Compute R_ij = I + [v]_x + [v]_x^2
    rotation = np.identity(3) + v_cross + v_cross @ v_cross * c

    return rotation


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
    ports_to_center = dict(map(lambda x: (x.name, np.array(x.dcenter)), ports))

    hfss_variables = {}

    points = component.get_polygons_points()[1][0].tolist()

    if config.tolerance > 0:
        simplified = shapely.simplify(
            shapely.Polygon(points), tolerance=config.tolerance
        )
        points = list(simplified.exterior.coords)

        ports_to_center = dict(
            map(
                lambda x: (x[0], np.array(find_new_port_location(x[1], simplified))),
                ports_to_center.items(),
            )
        )

    # if config.align_by == "port":
    center = ports_to_center.pop(config.port)
    align_by_port_var_name = config.port
    align_by_point = np.array(center)
    # elif config.align_by == "xmin":
    #     align_by_point = min(points, key=lambda x: x[0])
    #     align_by_port_var_name = "offset"
    # else:
    #     raise ValueError(f"Unidentified value for align by: {config.align_by=}")

    points = np.array(points)
    points -= align_by_point

    # extending to 3d
    length_of_points = points.shape[0]  # Number of vectors
    points = np.hstack((points, np.zeros((length_of_points, 1))))

    # get current orientation
    origin_angle = component.ports[config.port].orientation
    origin = np.array([np.cos(origin_angle), np.sin(origin_angle), 0])
    direction_to_vector = {
        "X": np.array([1, 0, 0]),
        "-X": np.array([-1, 0, 0]),
        "Y": np.array([0, 1, 0]),
        "-Y": np.array([0, -1, 0]),
        "Z": np.array([0, 0, 1]),
        "-Z": np.array([0, 0, -1])
    }

    target = direction_to_vector[config.orientation]
    rotation = construct_rotation(origin, target)

    # now do another rotation to align surface
    surface_orientation = config.surface_orientation
    if surface_orientation is None:
        surface_orientation_mapping = {
            "X": 'Z',
            "-X": 'Z',
            "Y": 'Z',
            "-Y": 'Z',
            "Z": '-Y',
            "-Z": 'Y'
        }
        surface_orientation = surface_orientation_mapping[config.orientation]

    origin = rotation @ direction_to_vector['Z']
    target = direction_to_vector[surface_orientation]
    second_rotation = construct_rotation(origin, target)
    rotation = second_rotation @ rotation

    # rotate
    rotated_points = np.einsum('ij, kj -> ki', rotation, points)

    # get offset value
    name = config.name
    unit = config.unit

    # adding all the ports to the hfss variables
    for k, v in ports_to_center.items():
        shifted_v = v - align_by_point
        rotated_v = rotation @ np.array([shifted_v[0], shifted_v[1], 0])
        hfss_variables[k] = tuple(rotated_v.tolist())

    # converting hfss_variables to x direction and y direction
    dependent_variables = {}
    for k, v in hfss_variables.items():
        dependent_variables[f"{name}_{k}_x"] = (
            f"{name}_{align_by_port_var_name}_x + {v[0]}{unit}"
        )
        dependent_variables[f"{name}_{k}_y"] = (
            f"{name}_{align_by_port_var_name}_y + {v[1]}{unit}"
        )

        dependent_variables[f"{name}_{k}_z"] = (
            f"{name}_{align_by_port_var_name}_z + {v[2]}{unit}"
        )

    # size
    size = rotated_points.max(axis=0) - rotated_points.min(axis=0)

    # adding the reference variable
    independent_variables = {
        f"{name}_{align_by_port_var_name}_x": f"0{unit}",
        f"{name}_{align_by_port_var_name}_y": f"0{unit}",
        f"{name}_{align_by_port_var_name}_z": f"0{unit}",
        f"{name}_size_x": f"{size[0]}{unit}",
        f"{name}_size_y": f"{size[1]}{unit}",
        f"{name}_size_z": f"{size[2]}{unit}"
    }

    points_as_string = [
        (
            f"{name}_{align_by_port_var_name}_x + {float(x)}um",
            f"{name}_{align_by_port_var_name}_y + {float(y)}um",
            f"{name}_{align_by_port_var_name}_z + {float(z)}um",
        )
        for x, y, z in rotated_points
    ]

    return points_as_string, independent_variables, dependent_variables


if __name__ == '__main__':
    origin = np.array([1, 0, 0])
    target = np.array([0, 1, 0])

    r = construct_rotation(origin, target)

    points = np.array([[1, 0, 0], [0.5, 0, 0]])

    rotated_points = np.einsum('ij, kj -> ki', r, points)

    print(1)
