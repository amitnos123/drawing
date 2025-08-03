from drawing import *
import matplotlib.pyplot as plt
import gdsfactory as gf

plotc = gf.Component()

j_layer = (11, 0)

p = PadConfig()
taper = TaperConfig(narrow_width = 15, length=50)
jun = RegularJunction(length=1, layer=j_layer)

# Build the transmon layout
# tr = TransmonConfig(taper=taper, junction=jun, pad=p).build() # component

tj = RegularJunction(length=10,width=1, gap=3)
bj = RegularJunction(length=10,width=1, gap=3)

squid = SquidConfig(top_junction=tj, bottom_junction=bj ).build()
plotc << squid
plotc.draw_ports()
plotc.pprint_ports()
plotc.plot()
plt.show()