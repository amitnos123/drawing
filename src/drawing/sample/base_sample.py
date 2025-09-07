from drawing.junction.base_junction import BaseJunctionConfig
from drawing.shared.utilities import SAMPLE_AREA_INDICATOR_LAYER
from pydantic import Field
from ..base_config import BaseConfig
import gdsfactory as gf

class BaseSampleConfig(BaseConfig):
    """
    Base configuration for sample components.
    Attributes:
        layer (LayerSpec): Layer specification for the sample.
        length (float): Length of the sample area.
        width (float): Width of the sample area.
        layer_area_indicator (LayerSpec): Layer specification for the area indicator.
    """
    length: float = 0
    width: float = 0
    name: str = ""

    layer_area_indicator: gf.typings.LayerSpec = Field(SAMPLE_AREA_INDICATOR_LAYER, exclude=True)

    def get_jopherson_junctions(self) -> list[BaseJunctionConfig]:
        return []

    def get_resistance_measurement_points(self) -> list[tuple[float, float]]:
        return []
    
    def getData(self) -> dict:
        dataSample = {}

        samplesJJData = []
        nameCountJJ = 1
        for sJJ in self.get_jopherson_junctions():
            dataJJ = {}
            dataJJ["type"] = sJJ.junction_type
            dataJJ["gap"] = sJJ.gap_length
            dataJJ["name"] = ""
            for n in range(nameCountJJ // 26): # There are 26 letters in the alphabet
                dataJJ["name"] += "A"
            if nameCountJJ % 26 > 0:
                dataJJ["name"] += chr(ord("A") + (nameCountJJ % 26) - 1)
            elif len(dataJJ["name"]) == 0: # to not have empty name
                dataJJ["name"] = "-"
            samplesJJData.append(dataJJ)
            nameCountJJ += 1

        samplesRMPData = []
        nameCountRMP = 1
        for sRMP in self.get_resistance_measurement_points():
            dataRMP = {}
            dataRMP["point"] = "("+str(sRMP[0])+","+str(sRMP[1])+")"
            dataRMP["name"] = ""
            for n in range(nameCountRMP // 26): # There are 26 letters in the alphabet
                dataRMP["name"] += "A"
            if nameCountRMP % 26 > 0:
                dataRMP["name"] += chr(ord("A") + (nameCountRMP % 26) - 1)
            elif len(dataRMP["name"]) == 0: # to not have empty name
                dataRMP["name"] = "-"
            samplesRMPData.append(dataRMP)
            nameCountRMP += 1

        dataSample["name"] = self.name
        dataSample["dimension"] = [self.length, self.width]
        dataSample["center"] = [0,0]
        dataSample["jopherson junctions"] = samplesJJData
        dataSample["resistance measurement points"] = samplesRMPData

        return dataSample