from pydantic import BaseModel
from typing import Literal


class ExportConfig(BaseModel):
    """
    Configuration for the meander_euler function.
    """

    name: str
    orientation: Literal['X', 'Y', 'Z', '-X', '-Y', '-Z'] = 'Z'
    port: str
    unit: str = "um"
    # align_by_port: bool = True
    tolerance: float = 0
    surface_orientation: Literal['X', 'Y', 'Z', '-X', '-Y', '-Z'] | None = None
    add_ports_as_variables: bool = True
