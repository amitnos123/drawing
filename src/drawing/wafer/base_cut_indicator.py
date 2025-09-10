from ..base_config import BaseConfig
import gdsfactory as gf

class BaseCutIndicatorConfig(BaseConfig):
    """
    Base Cut Indicator configuration for creating a rectangular cut indicator on a wafer layout.
    Attributes:
        gap (float): Gap between the cut indicators in micrometers.
        width (float): Width of the cut indicator in micrometers.
        length (float): Length of the cut indicator in micrometers.
    """

    gap: float = 100
    width: float = 300
    length: float = 300

    def validate(self) -> None:
        if self.gap < 0:
            raise ValueError(
                "Base Cut Indicator Config gap be greater than or equal to zero."
            )
        if self.width < 0:
            raise ValueError(
                "Base Cut Indicator Config height be greater than or equal to zero."
            )
        if self.length < self.gap:
            raise ValueError(
                "Base Cut Indicator Config width be greater than or equal to gap."
            )