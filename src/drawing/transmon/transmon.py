from drawing.junction import BaseJunctionConfig, SymmetricJunctionConfig
import gdsfactory as gf
import gdsfactory.components as gc
from ..shared import smooth_corners, merge_referenced_shapes
from typing import TypeVar, Type
import matplotlib.pyplot as plt
from typing_extensions import Self
from pydantic import ConfigDict, Field, model_validator
from pydantic import computed_field
from pyparsing import cached_property
from ..base_config import BaseConfig
from . import TaperConfig, PadConfig
from .antenna import AntennaConfig
import gdsfactory as gf


class IntegrationConfig(BaseConfig):
    feature_radius: float = 10.0
    use_antenna: bool = True

    model_config = ConfigDict(frozen=True)


T = TypeVar('T', bound=BaseConfig)


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


class TransmonConfig(BaseConfig):
    """
    """
    integration_config: IntegrationConfig = IntegrationConfig()
    pad: PadConfig = PadConfig()
    taper: TaperConfig = TaperConfig()
    junction: BaseJunctionConfig = SymmetricJunctionConfig(layer=(11,11))
    antenna: AntennaConfig = AntennaConfig()
    validate_assignment: bool = Field(False, exclude=True)

    juction_taper_overlap: float = 3

    model_config = ConfigDict(frozen=True)

    def build(self) -> gf.Component:
        return TransmonConfig._build(
            # integration_config=self.integration_config,
            pad=self.pad.build().copy(),
            taper=self.taper.build().copy(),
            junction=self.junction.build().copy(),
            antenna=self.antenna.build().copy(),
            layer=self.layer,
            juction_taper_overlap=self.juction_taper_overlap,
            taper_narrow_width=self.taper.narrow_width,
            pad_width=self.pad.width,

            
            junction_right_connecting_port=self.junction.RIGHT_CONNECTING_PORT_NAME,
            junction_left_connecting_port=self.junction.LEFT_CONNECTING_PORT_NAME,
            pad_right_connecting_port=self.pad.RIGHT_CONNECTING_PORT_NAME,
            taper_wide_connecting_port=self.taper.WIDE_CONNECTING_PORT_NAME,
            taper_narrow_connecting_port=self.taper.NARROW_CONNECTING_PORT_NAME,
            antenna_start_port=self.antenna.ANTENNA_START_PORT,
        )

    @gf.cell
    @staticmethod
    def _build(
        # integration_config: IntegrationConfig,
        pad: gf.Component,
        taper: gf.Component,
        junction: gf.Component,
        antenna: gf.Component,
        layer,
        juction_taper_overlap: float,
        junction_right_connecting_port: str,
        junction_left_connecting_port: str,
        pad_right_connecting_port: str,
        taper_wide_connecting_port: str,
        taper_narrow_connecting_port: str,
        antenna_start_port: str ,
        taper_narrow_width: float,
        pad_width: float
    ) -> gf.Component:
        pt = gf.Component()

        pad_ref = pt << pad
        taper_ref = pt << taper

        pad_ref.connect(pad_right_connecting_port, taper_ref.ports[taper_wide_connecting_port], allow_width_mismatch=True)


        pt = smooth_corners(merge_referenced_shapes(pt)).copy()
        
        pt_right = pt.copy().mirror_x()

        pt_right.add_port(name="right_junction_connection", center=(pt_right.xmin,0), width=taper_narrow_width, orientation=180, layer=layer, port_type="electrical")
        pt_right.add_port(name="antenna_connection", center=(pt_right.xmax,0), width=pad_width, layer=layer, port_type="electrical")

        pt.add_port(name="left_junction_connection", port=taper_ref.ports[taper_narrow_connecting_port])

        c = gf.Component()

        pt_right_ref = c << pt_right
        pt_left_ref = c << pt

        junction_ref = c << junction

        pt_left_ref.connect("left_junction_connection", junction_ref.ports[junction_right_connecting_port], allow_layer_mismatch=True)
        pt_right_ref.connect("right_junction_connection", junction_ref.ports[junction_left_connecting_port], allow_layer_mismatch=True)

        pt_left_ref.movex(-juction_taper_overlap)
        pt_right_ref.movex(juction_taper_overlap)

        antenna_ref = c << antenna

        antenna_ref.connect(antenna_start_port, pt_right_ref.ports["antenna_connection"], allow_width_mismatch=True)

        return merge_referenced_shapes(c.mirror_x())

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
        # self.antenna.validate()

        # # pad-taper validation
        # #-------------------------------------------------------------------
        # if self.pads_distance < self.taper.length * 2:
        #     raise ValueError(
        #         f"Pad distance {self.pad.distance} must be greater than the taper length (2x) {self.taper.length * 2} "
        #     )
        
        # if self.pad.width < self.taper.narrow_width:
        #     raise ValueError(
        #         f"Pad width {self.pad.width} must be greater than the taper narrow width {self.taper.narrow_width}"
        #     )
        
        # # taper-taper validation
        # #-------------------------------------------------------------------
        # if self.taper.wide_width < self.taper.narrow_width:
        #     raise ValueError(
        #         f"Taper wide width {self.taper.wide_width} must be greater than the taper narrow width {self.taper.narrow_width}"
        #     )
        

        # # taper-junction validation
        # #-------------------------------------------------------------------
        # if self.taper.narrow_width < self.junction.width:
        #     raise ValueError(
        #         f"Taper narrow width {self.taper.narrow_width} must be greater than the junction width {self.junction.width}"
        #     )
        
        # # pads-taper-junction validation
        # #-------------------------------------------------------------------
        # if self.pad.distance < self.junction.length + self.junction.gap + self.taper.length * 2:
        #     raise ValueError(
        #         f"Pad distance {self.pad.distance} must be greater than the junction length {self.junction.length} "
        #         f"plus taper length (2x) {self.taper.length * 2}"
        #     )
        return self