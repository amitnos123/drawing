from ..base_config import BaseConfig

class BaseJunctionConfig(BaseConfig):
    """
    Base configuration for junction components.
    Attributes:
        layer (LayerSpec): Layer specification for the junction component.
    """
    
    gap_length: float = 1.0
    
    def total_length(self) -> float:
        """
        Returns the total length of the junction.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def validate(self) -> None:
        if self.left_arm is None: 
            raise ValueError("Left arm must be defined.")
        if self.right_arm is None:
            raise ValueError("Right arm must be defined.")