from pydantic import BaseModel
from typing import Literal


class ExportConfig(BaseModel):
    """
    Configuration for the meander_euler function.
    """

    name: str
    unit: str = "um"
    align_by: Literal["xmin", "port"] = "xmin"
    tolerance: float = 0
    port: str | None = None
    add_ports_as_variables: bool = True
