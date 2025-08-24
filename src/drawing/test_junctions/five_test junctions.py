from drawing.transmon.transmon import TransmonConfig
from ..base_config import BaseConfig
import gdsfactory as gf

class FiveTestJunctionsConfig(BaseConfig):
    
    gap_start_length: float = 1.0
    gap_end_length: float = 5.0
    transmonConfig: TransmonConfig = TransmonConfig()

    def build(self) -> gf.Component:
        return FiveTestJunctionsConfig.fiveTestJunctionsConfig()
    
    @gf.cell
    @staticmethod
    def fiveTestJunctionsConfig() -> gf.Component:
        c = gf.Component()
        return c

    def getData(self) -> list:
        # test junctions:
        #   type:
        #       DOLAN
        #       DOLATHAN
        #       MANHANTAN
        #    BRIDGE START GAP
        #    BRIDGE END GAP
        #    FINGER WIDTH
        rtn = []
        rtn["type"] = self.transmonConfig.junction.junction_type
        rtn["BRIDGE START GAP"] = self.gap_start_length
        rtn["BRIDGE END GAP"] = self.gap_end_length
        rtn["LEFT FINGER"] = self.transmonConfig.junction.get_left_arm_config().model_dump_json()
        rtn["RIGHT FINGER"] = self.transmonConfig.junction.get_right_arm_config().model_dump_json()
        return rtn

    def validate(self) -> None:
        pass