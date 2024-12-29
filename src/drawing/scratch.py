from src.deprecated import meander

if __name__ == "__main__":
    # euler = meander.meander_euler()
    # print(has_overlapping_polygons(euler))
    # print(has_invalid_polygons(euler))
    # print(verify_shape_continuity(euler))
    # meander.meander_euler().write_gds('gds_files\\meander_euler.gds', with_metadata=False)
    meander_inst = meander.meander_optimal_turn()
    # meander.meander_optimal_turn().write_gds('gds_files\\meander_optimal.gds', with_metadata=False)
    # transmon.draw_transmon(feature_radius=5, pad_radius=200).write_gds('gds_files\\transmon.gds', with_metadata=False)
    print(1)

    import shapely
    import json
    import numpy as np

    polygon = meander_inst.get_polygons_points()[1][0]
    simplified = shapely.simplify(shapely.Polygon(polygon), tolerance=1e-3)
    points = list(simplified.exterior.coords)
    print(len(points))

    point_by_xmin = min(points, key=lambda x: x[0])

    points = np.array(points)
    points -= point_by_xm

    points_lst = points.tolist()
    # polygon.x

    hfss_points = [
        [f"offset_x + {x}mm", f"offset_y + {y}mm", "0mm"] for x, y in points_lst
    ]
    path = r"D:\Weizmann Institute Dropbox\Goldblatt Uri\Quantum Circuits Lab\Uri\DualRailErasure\gds_files\points.json"
    with open(path, "w") as f:
        json.dump({"points": hfss_points}, f)
