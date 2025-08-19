from ..base_config import BaseConfig
import gdsfactory as gf

class WaferConfig(BaseConfig):

    radius: float = 76200 # 3 inch in micro meter
    safe_radius: float = 71120 # 2.9 inch in micro meter
    safe_layer: gf.typings.LayerSpec | None = None

    def build(self) -> gf.Component:
        return WaferConfig._build(
            radius=self.radius,
            safe_radius=self.safe_radius,
            layer=self.layer,
            safe_layer=self.safe_layer
        )

    @staticmethod
    @gf.cell
    def _build(
        radius: float,
        safe_radius: float,
        layer: gf.typings.LayerSpec,
        safe_layer: gf.typings.LayerSpec | None,
    ) -> gf.Component:
        c = gf.Component()

        c << gf.components.circle(radius=radius, layer=layer)
        if safe_layer != None:
            c << gf.components.circle(radius=safe_radius, layer=safe_layer)

        return c
    
    def validate(self) -> None:
        if self.radius < 0:
            raise ValueError(
                "Wafer radius be greater than or equal to zero."
            )