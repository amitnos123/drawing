from pydantic import BaseModel, ConfigDict, computed_field
import gdsfactory as gf
from pyparsing import cached_property
from .shared import DEFAULT_LAYER
class BaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """
    Base configuration for drawing components.
    Attributes:
        component (gf.Component | None): The GDS component to be drawn.
        layer (LayerSpec): Layer specification for the component.
    """
    layer: gf.typings.LayerSpec = DEFAULT_LAYER

    @computed_field
    @cached_property
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
    