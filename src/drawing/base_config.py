from pydantic import BaseModel
import gdsfactory as gf
from .shared import DEFAULT_LAYER
class BaseConfig(BaseModel):
    """
    Base configuration for drawing components.
    Attributes:
        component (gf.Component | None): The GDS component to be drawn.
        layer (LayerSpec): Layer specification for the component.
    """
    layer: gf.typings.LayerSpec = DEFAULT_LAYER

    def build(self) -> gf.Component:
        """
        Builds the GDS component based on the configuration.
        Returns:
            gf.Component: The GDS component.
        """
        raise NotImplementedError("Subclasses should implement build(self) method.")
    
    def clone(self) -> "BaseConfig":
        """
        Clones the configuration.
        Returns:
            BaseConfig: A new instance of the configuration with the same attributes.
        """
        return self.model_copy(deep=True)
    
    def validate(self) -> None:
        pass
    