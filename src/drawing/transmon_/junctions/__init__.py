from .regular import RegularJunction
from .irregular import IrregularJunction
from typing import Annotated
from pydantic import TypeAdapter, Field

SupportedJunctions = Annotated[RegularJunction | IrregularJunction, Field(discriminator='type')]
JunctionAdapter = TypeAdapter(SupportedJunctions)