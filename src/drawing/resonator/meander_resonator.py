
from drawing.resonator.base_resonator import BaseResonator
import gdsfactory as gf

class MeanderResonator(BaseResonator):
    """
    """

    def build(self) -> gf.Component:
        return MeanderResonator.meanderResonator()

    @staticmethod
    @gf.cell
    def meanderResonator() -> gf.Component:
        c = gf.Component
        return c
    
    def validate(self) -> None:
        pass