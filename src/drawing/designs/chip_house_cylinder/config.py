from pydantic import BaseModel
from typing import Literal


class Variable(BaseModel):
    name: str
    value: float
    unit: str = ''

    def to_string(self):
        return f'{self.value}{self.unit}'


class ChipHouseCylinderConfig(BaseModel):
    type: Literal['chip_house_cylinder'] = 'chip_house_cylinder'

    spacer_length: Variable
    chip_house_length: Variable
    chip_house_radius: Variable

    chip_base_length: Variable
    chip_base_thickness: Variable
    chip_base_width: Variable
    chip_base_material: str

    pin_waveguide_radius: Variable
    pin_waveguide_length: Variable
    pin_conductor_radius: Variable

    pin_a_location: Variable
    pin_b_location: Variable
    pin_c_location: Variable
    pin_c_length: Variable
    pin_d_location: Variable

    meander_type: str
    meander_args: dict


    def get_variables(self):
        def _helper():
            for attr_name, attr_value in self.__dict__.items():
                if isinstance(attr_value, Variable):
                    yield attr_value

        return list(_helper())
