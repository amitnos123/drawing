import meander
import transmon

if __name__ == '__main__':
    # meander.meander_euler().write_gds('meander_euler.gds', with_metadata=False)
    # meander.meander_optimal_turn().write_gds('meander_optimal.gds', with_metadata=False)
    transmon.draw_transmon(feature_radius=5, pad_radius=200).write_gds('transmon.gds', with_metadata=False)
