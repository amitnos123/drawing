
from drawing.resonator.base_resonator import BaseResonatorConfig
import gdsfactory as gf

class MeanderResonatorConfig(BaseResonatorConfig):
    """
    Configuration for a meander resonator component.
    Attributes:
        layer (LayerSpec): Layer specification for the meander resonator component.
    """

    def build(self) -> gf.Component:
        return MeanderResonatorConfig.meanderResonator()

    @staticmethod
    @gf.cell
    def meanderResonator() -> gf.Component:
        c = gf.Component()
        return c
    
    def validate(self) -> None:
        pass