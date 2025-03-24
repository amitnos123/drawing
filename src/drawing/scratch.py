from src.deprecated import meander
from src.drawing.transmon import transmon
import matplotlib.pyplot as plt
from src.drawing.transmon.transmon import TransmonConfig

if __name__ == "__main__":
    # euler = meander.meander_euler()
    # print(has_overlapping_polygons(euler))
    # print(has_invalid_polygons(euler))
    # print(verify_shape_continuity(euler))
    # meander.meander_euler().write_gds('gds_files\\meander_euler.gds', with_metadata=False)
    # meander_inst = meander.meander_optimal_turn()
    # meander.meander_optimal_turn().write_gds('gds_files\\meander_optimal.gds', with_metadata=False)
    # transmon.draw_transmon(feature_radius=5, pad_radius=200).write_gds('gds_files\\transmon.gds', with_metadata=False)
    print(1)

    #


    # tr = transmon.draw_transmon(feature_radius=10, pad_radius=100)
    # tr = transmon.draw_transmon_with_antenna(feature_radius=10, pad_radius=100)
    tr = TransmonConfig().build()
    # tr.pprint_ports()
    tr.draw_ports()
    tr.write_gds('gds_files\\testing.gds', with_metadata=False)
    tr.plot()
    plt.show()

