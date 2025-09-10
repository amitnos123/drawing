from .base_align_cross import BaseAlignCrossConfig
import gdsfactory as gf

class LaserAlignCrossConfig(BaseAlignCrossConfig):
    def validate(self) -> None:
        super().validate()