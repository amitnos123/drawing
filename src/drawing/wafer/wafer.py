import datetime
import json
from drawing.sample.base_sample import BaseSampleConfig
from drawing.test_junctions.base_test_junctions import BaseTestJunctionsConfig
from drawing.shared.utilities import DEFAULT_WAFER_LAYER

from create_directory import create_design_json
from ..base_config import BaseConfig
import gdsfactory as gf

class WaferConfig(BaseConfig):

    layer: gf.typings.LayerSpec = DEFAULT_WAFER_LAYER
    radius: float = 76200 # 3 inch in micro meter
    safe_radius: float = 71120 # 2.9 inch in micro meter
    safe_layer: gf.typings.LayerSpec | None = None

    samples: list[BaseSampleConfig] = []
    testJunctions: list[BaseTestJunctionsConfig] = []

    wafer_design: str = ""

    def build(self) -> gf.Component:
        return WaferConfig.wafer(
            radius=self.radius,
            safe_radius=self.safe_radius,
            layer=self.layer,
            safe_layer=self.safe_layer
        )

    @staticmethod
    @gf.cell
    def wafer(
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
    
    def create_design_json(self,  material: str,  thickness: float, recipe: str) -> str:
        dataSamples = []
        for s in self.samples:
            dataSamples.append(s.getData())

        testJunctionsData = []
        for tJ in self.testJunctions:
            testJunctionsData.append(tJ.getData())
            
        return create_design_json(
            wafer_name=self.get_wafer_name(),
            wafer_material=material,
            wafer_size=self.radius,
            wafer_thickness=thickness,
            recipe=recipe,
            samples=dataSamples,
            test_junctions=testJunctionsData
        )
    
    def get_wafer_name(self) -> str:
        x = datetime.datetime.now()
        return x.strftime("%Y") + x.strftime("%m") + x.strftime("%d") + "_" + self.wafer_design

    def validate(self) -> None:
        if self.radius < 0:
            raise ValueError(
                "Wafer radius be greater than or equal to zero."
            )