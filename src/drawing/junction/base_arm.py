from ..base_config import BaseConfig
import gdsfactory as gf

class BaseArmConfig(BaseConfig):
    """
    Base configuration for junction components.
    Attributes:
        layer (LayerSpec): Layer specification for the junction component.
    """

    def build(self) -> gf.Component:
        raise NotImplementedError("Subclasses should implement this method.")

    def total_length(self) -> float:
        """
        Returns the total length of the arm.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")
    
    def validate(self) -> None:
        pass