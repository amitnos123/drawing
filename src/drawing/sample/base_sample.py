from ..base_config import BaseConfig
import gdsfactory as gf

class BaseSampleConfig(BaseConfig):

    def build(self) -> gf.Component:
        return BaseSampleConfig._build(
            layer=self.layer
        )

    @staticmethod
    @gf.cell
    def _build(
        layer: gf.typings.LayerSpec,
    ):
        c = gf.Component()

        return c