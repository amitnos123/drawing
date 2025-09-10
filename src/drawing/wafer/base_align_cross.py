from ..base_config import BaseConfig
import gdsfactory as gf

class BaseAlignCrossConfig(BaseConfig):
    def validate(self) -> None:
        super().validate()