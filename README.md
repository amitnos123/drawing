# Transmon Layout Library

This repository provides a Python library for designing custom transmon layouts using [gdsfactory](https://github.com/gdsfactory/gdsfactory). The library integrates several configurable components—such as pads, tapers, junctions, and an optional antenna—into a unified layout via the `TransmonConfig` class.

## Overview

The `TransmonConfig` class encapsulates all the parameters required to build a transmon layout. It manages the integration of sub-components, including:
- **Pads**: For electrical connections.
- **Tapers**: To transition between different geometries.
- **Junctions**: For connecting tapers to pads.
- **Antenna (Optional)**: For additional functionality.

This configuration simplifies complex layout creation by automatically handling port connections, merging of shapes, and corner smoothing.

## Installation
   ```bash
   git clone https://github.com/HutoriHunzu/drawing.git
   pip install -e drawing
```

## Usage
This module is specified for the creation of transmons and exporting them to HFSS using
pyaedt. An example for creating a transmon:
```python

import matplotlib.pyplot as plt
from drawing import TransmonConfig
# Build the transmon layout
tr = TransmonConfig().build()

# Optionally, print port information (uncomment if needed)
# tr.pprint_ports()

# Visualize the ports on the component
tr.draw_ports()

# Write the layout to a GDS file (without metadata)
tr.write_gds('gds_files/testing.gds', with_metadata=False)

# Plot the layout and show the figure
tr.plot()
plt.show()
```
One could also modify the configuration by adding different values for the attributes
for example:

```python

import matplotlib.pyplot as plt
from drawing import TransmonConfig
from drawing.transmon import IntegrationConfig
# Build the transmon layout
integration_config = IntegrationConfig(use_antenna=False)
tr = TransmonConfig(integration_config=integration_config).build()

# Visualize the ports on the component
tr.draw_ports()

# Write the layout to a GDS file (without metadata)
tr.write_gds('gds_files/testing.gds', with_metadata=False)

# Plot the layout and show the figure
tr.plot()
plt.show()
```
Now there won't be antenna in the transmon.
