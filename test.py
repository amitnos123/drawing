from drawing import *
import matplotlib.pyplot as plt
import gdsfactory as gf

plotc = gf.Component()

squid = SquidConfig().build()
plotc << squid
plotc.draw_ports()
plotc.pprint_ports()
plotc.plot()
plt.show()