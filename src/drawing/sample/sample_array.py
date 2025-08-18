from .base_sample import BaseSampleConfig
from ..base_config import BaseConfig
import gdsfactory as gf

class sampleArrayConfig(BaseConfig):

    sample: BaseSampleConfig

    def build(self) -> gf.Component:
        return sampleArrayConfig._build(
            sample=self.sample,
            layer=self.layer
        )

    @staticmethod
    @gf.cell
    def _build(
        sample: BaseSampleConfig,
        layer: gf.typings.LayerSpec,
    ):
        c = gf.Component()

        return c