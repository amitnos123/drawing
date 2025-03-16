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
    integration_config: IntegrationConfig = IntegrationConfig()
    pad: PadConfig = PadConfig()
    taper: TaperConfig = TaperConfig()
    junction: SupportedJunctions = RegularJunction()
    antenna: AntennaConfig = AntennaConfig()

    layer: LayerSpec = DEFAULT_LAYER

    def build(self):
        c = gf.Component()

        # Build pads
        left_pad, right_pad = self.pad.build(c)

        # return c

        # Build tapers
        left_taper, right_taper = self.taper.build(c)

        # if antenna
        if self.integration_config.use_antenna:
            self.antenna.build(c)
        # integrating all
        self.junction.connect_tapers_to_pads(left_pad, right_pad, left_taper, right_taper)

        # merging
        c = self.smooth_and_merge(c, left_taper, right_taper)

        c = self.junction.build(c)

        return merge_referenced_shapes(c)

    def smooth_and_merge(self, c, left_taper, right_taper):
        if self.integration_config.feature_radius > 0:
            port = left_taper.ports['narrow_end']
            center = port.center
            center = center[0] // 1000 - self.integration_config.feature_radius / 2, center[1] // 1000
            width = port.width // 1000
            c.add_port('left_narrow_end',
                       center=center,
                       port_type='electrical',
                       layer=self.layer,
                       width=width,
                       orientation=0)
            #
            port = right_taper.ports['narrow_end']
            center = port.center
            center = center[0] // 1000 + self.integration_config.feature_radius / 2, center[1] // 1000
            width = port.width // 1000

            c.add_port('right_narrow_end',
                       center=center,
                       port_type='electrical',
                       layer=self.layer,
                       width=width,
                       orientation=180)

            c = merge_referenced_shapes(c)
            c = smooth_corners(c, radius=self.integration_config.feature_radius)

            # adding another compass to make sharp edges at the end
            w = gf.Component()
            compass = gc.compass((self.integration_config.feature_radius / 2, self.taper.narrow_width),
                                 layer=self.layer)

            ref = w << c

            left_ref = w << compass
            right_ref = w << compass

            left_ref.connect('e1', ref.ports['left_narrow_end'])
            right_ref.connect('e3', ref.ports['right_narrow_end'])

            w.add_ports(list(filter(lambda x: x.name not in ('left_narrow_end',
                                                             'right_narrow_end'), ref.ports)))
            w.add_port('left_narrow_end', left_ref.ports['e3'])
            w.add_port('right_narrow_end', right_ref.ports['e1'])

            return merge_referenced_shapes(w)

        else:

            c.add_port('left_narrow_end', left_taper.ports['narrow_end'])
            c.add_port('right_narrow_end', right_taper.ports['narrow_end'])

            return merge_referenced_shapes(c)

    @classmethod
    def load_from_flat_dict(cls, d: dict):

        nested_dict = create_nested_from_flat_by_prefix(prefixes=['integration_config', 'pad',
                                                                  'antenna', 'taper', 'junction'],
                                                        d=d)


        nested_dict['junction']['type'] = nested_dict['junction'].get('type', 'regular')
        # integration_config = load_relevant_parameters(d, IntegrationConfig, 'integration_config_')
        # pad = load_relevant_parameters(d, PadConfig, 'pad_')
        # antenna = load_relevant_parameters(d, AntennaConfig, 'antenna')
        # taper_config = load_relevant_parameters(d, TaperConfig, 'taper_')
        # junction_config = load_relevant_parameters(d, JunctionAdapter, 'junction_')

        return TransmonConfig(**nested_dict)
