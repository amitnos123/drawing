from drawing.transmon.junctions.base_junction import BaseJunction
from .pads import PadConfig
from .tapers import TaperConfig
from .antenna import AntennaConfig
from .junctions import SupportedJunctions, RegularJunction, JunctionAdapter
from gdsfactory.typings import LayerSpec
from pydantic import BaseModel
import gdsfactory as gf
import gdsfactory.components as gc
from ..shared import DEFAULT_LAYER, smooth_corners, merge_referenced_shapes
from typing import TypeVar, Type
import matplotlib.pyplot as plt
from typing_extensions import Self
from pydantic import model_validator


class IntegrationConfig(BaseModel):
    feature_radius: float = 10.0
    use_antenna: bool = True


T = TypeVar('T', bound=BaseModel)


def load_relevant_parameters(parameters: dict, cls: Type[T], with_prefix: str = None) -> T:
    if with_prefix:
        parameters = {k[len(with_prefix):]: v
                      for k, v in filter(lambda x: x[0].startswith(with_prefix), parameters.items())}

    relevant_parameters_names = set(cls.model_fields.keys()) & set(parameters.keys())
    relevant_parameters = {k: parameters[k] for k in relevant_parameters_names}
    return cls(**relevant_parameters)


def create_nested_from_flat_by_prefix(prefixes: list[str], d: dict):
    result = {}
    for prefix in prefixes:
        parameters = {k.replace(f'{prefix}_', ''): d[k] for k in filter(lambda x: x.startswith(f'{prefix}_'), d.keys())}
        # filter none
        parameters = {k: v for k, v in parameters.items() if v is not None}
        result[prefix] = parameters
    return result


class TransmonConfig(BaseModel):
    """
    Configuration for constructing a complete transmon layout using GDSFactory.

    This configuration encapsulates parameters for integrating pads, tapers, junctions,
    and an optional antenna. It manages shape merging, smoothing of corners, and the overall
    connectivity required to build a transmon component.

    Attributes:
        integration_config (IntegrationConfig): Settings controlling integration features
            such as feature radius and antenna usage.
        pad (PadConfig): Configuration parameters for pad dimensions and layout.
        taper (TaperConfig): Configuration for taper shapes.
        junction (SupportedJunctions): Junction configuration that connects tapers to pads.
            Defaults to a regular junction.
        antenna (AntennaConfig): Configuration for the optional antenna shape.
        layer (LayerSpec): GDS layer specification applied to all components.
    """
    integration_config: IntegrationConfig = IntegrationConfig()
    pad: PadConfig = PadConfig()
    taper: TaperConfig = TaperConfig()
    junction: BaseJunction = RegularJunction()
    antenna: AntennaConfig = AntennaConfig()
    layer: LayerSpec = DEFAULT_LAYER
    validate_assignment: bool = True

    def build(self) -> gf.Component:
        """
        Builds the complete transmon component.

        This method performs the following steps:
          1. Constructs pads and tapers.
          2. Optionally builds and connects an antenna.
          3. Uses the junction configuration to connect tapers to pads.
          4. Merges and smooths shapes as specified in the integration configuration.

        Returns:
            gf.Component: The finalized transmon component with merged and smoothed shapes.
        """
        c = gf.Component()

        # Build pads 
        left_pad, right_pad = self.pad.build(c)

        # Build tapers
        left_taper, right_taper = self.taper.build(c)


        # Optionally add the antenna to the layout.
        if self.integration_config.use_antenna:
            self.antenna.build(c)


        # Connect tapers to pads using the junction configuration.
        self.junction.connect_tapers_to_pads(left_pad, right_pad, left_taper, right_taper)


        # Merge and smooth the shapes if needed.
        c = self.smooth_and_merge(c, left_taper, right_taper)
        c = self.junction.build(c)

        return merge_referenced_shapes(c)

    def smooth_and_merge(self, c: gf.Component, left_taper, right_taper) -> gf.Component:
        """
        Applies smoothing and shape merging to the component.

        If a positive feature radius is set in the integration configuration, the function
        creates new ports based on the tapers’ narrow ends, merges shapes, and smooths the corners.
        Otherwise, it directly adds the taper ports.

        Args:
            c (gf.Component): The component to process.
            left_taper: The left taper sub-component.
            right_taper: The right taper sub-component.

        Returns:
            gf.Component: The processed component with updated ports and merged shapes.
        """
        if self.integration_config.feature_radius > 0:
            # Adjust left port coordinates.
            port = left_taper.ports['narrow_end']
            center = port.center
            center = (center[0] - self.integration_config.feature_radius / 2, center[1])
            width = port.width
            c.add_port(
                'left_narrow_end',
                center=center,
                port_type='electrical',
                layer=self.layer,
                width=width,
                orientation=0
            )

            # Adjust right port coordinates.
            port = right_taper.ports['narrow_end']
            center = port.center
            center = (center[0] + self.integration_config.feature_radius / 2, center[1])
            width = port.width
            c.add_port(
                'right_narrow_end',
                center=center,
                port_type='electrical',
                layer=self.layer,
                width=width,
                orientation=180
            )

            c = merge_referenced_shapes(c)
            c = smooth_corners(c, radius=self.integration_config.feature_radius)

            # Add a compass to sharpen the end connections.
            w = gf.Component()
            compass = gc.compass(
                (self.integration_config.feature_radius / 2, self.taper.narrow_width),
                layer=self.layer
            )
            ref = w << c
            left_ref = w << compass
            right_ref = w << compass

            left_ref.connect('e1', ref.ports['left_narrow_end'])
            right_ref.connect('e3', ref.ports['right_narrow_end'])

            # Preserve existing ports except for the narrow_end ports.
            w.add_ports([p for p in ref.ports if p.name not in ('left_narrow_end', 'right_narrow_end')])
            w.add_port('left_narrow_end', port=left_ref.ports['e3'])
            w.add_port('right_narrow_end', port=right_ref.ports['e1'])

            return merge_referenced_shapes(w)

        # When no smoothing is required, simply propagate the taper ports.
        c.add_port('left_narrow_end', port=left_taper.ports['narrow_end'])
        c.add_port('right_narrow_end', port=right_taper.ports['narrow_end'])
        return merge_referenced_shapes(c)

    @classmethod
    def load_from_flat_dict(cls, d: dict) -> "TransmonConfig":
        """
        Creates a TransmonConfig instance from a flat dictionary of parameters.

        The function splits the flat dictionary into nested dictionaries based on predefined prefixes
        and instantiates the TransmonConfig.

        Args:
            d (dict): Flat dictionary containing configuration parameters.

        Returns:
            TransmonConfig: A configuration instance built from the provided dictionary.
        """
        nested_dict = create_nested_from_flat_by_prefix(
            prefixes=['integration_config', 'pad', 'antenna', 'taper', 'junction'],
            d=d
        )
        nested_dict['junction']['type'] = nested_dict['junction'].get('type', 'regular')
        return TransmonConfig(**nested_dict)

    @model_validator(mode='after')
    def validate_components(self) -> Self:
        """
        Validates the configuration of the transmon components.
        This method checks the parameters of the pad, taper, junction, and antenna components
        to ensure they meet the required conditions for a valid transmon layout.
        Raises:
            ValueError: If any of the validation checks fail.
        """
        # Skip validation if validate_assignment is False
        if not self.validate_assignment:
            return self
        
        # Validate individual components
        self.pad.validate()
        self.taper.validate()
        self.junction.validate()
        self.antenna.validate()

        # pad-taper validation
        #-------------------------------------------------------------------
        if self.pad.distance < self.taper.length * 2:
            raise ValueError(
                f"Pad distance {self.pad.distance} must be greater than the taper length (2x) {self.taper.length * 2} "
            )
        
        if self.pad.width < self.taper.narrow_width:
            raise ValueError(
                f"Pad width {self.pad.width} must be greater than the taper narrow width {self.taper.narrow_width}"
            )
        
        # taper-taper validation
        #-------------------------------------------------------------------
        if self.taper.wide_width < self.taper.narrow_width:
            raise ValueError(
                f"Taper wide width {self.taper.wide_width} must be greater than the taper narrow width {self.taper.narrow_width}"
            )
        

        # taper-junction validation
        #-------------------------------------------------------------------
        if self.taper.narrow_width < self.junction.width:
            raise ValueError(
                f"Taper narrow width {self.taper.narrow_width} must be greater than the junction width {self.junction.width}"
            )
        
        # pads-taper-junction validation
        #-------------------------------------------------------------------
        if self.pad.distance < self.junction.length + self.junction.gap + self.taper.length * 2:
            raise ValueError(
                f"Pad distance {self.pad.distance} must be greater than the junction length {self.junction.length} "
                f"plus taper length (2x) {self.taper.length * 2}"
            )
        return self