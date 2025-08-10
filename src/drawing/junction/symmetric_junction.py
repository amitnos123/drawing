import gdsfactory as gf
from .base_junction import BaseJunctionConfig
from .base_arm import BaseArmConfig
from .regular_arm import RegularArmConfig
from pydantic import computed_field
from functools import cached_property

class SymmetricJunctionConfig(BaseJunctionConfig):
    """
    Base configuration for symmetric junction components.
    Attributes:
        arm (BaseArmConfig): Configuration for the arm component.
        gap_length (float): Length of the gap between the arms.
        layer (LayerSpec): Layer specification for the junction component.
        gap_layer (LayerSpec): Layer specification for the gap.
        gap_create (bool): Whether to create a gap in the junction.
    """
        
    arm: BaseArmConfig = RegularArmConfig()

    @computed_field
    @cached_property
    def LEFT_CONNECTING_PORT_NAME(self) -> str:
        return self.LEFT_PREFIX + self.arm.CONNECTION_PORT_NAME
    
    @computed_field
    @cached_property
    def RIGHT_CONNECTING_PORT_NAME(self) -> str:
        return self.RIGHT_PREFIX + self.arm.CONNECTION_PORT_NAME

    @computed_field
    @cached_property
    def build(self) -> gf.Component:
        c = gf.Component()
        
        # Create left and right arms using the same arm configuration
        a = self.arm.build       

        right_arm_ref = c << a.copy()
        left_arm_ref = c << a.mirror_x()

        # Add validation that port "gap" exists in both arms

        # Connect the arms via ports
        left_arm_ref.connect(self.arm.GAP_PORT_NAME, right_arm_ref.ports[self.arm.GAP_PORT_NAME])
        # Position the right arm
        left_arm_ref.movex(-self.gap_length)

        if self.gap_create:
            # Create a gap in the junction
            gap = c << gf.components.rectangle(size=(self.gap_length, right_arm_ref.ymax - right_arm_ref.ymin), layer=self.gap_layer)
            gap.connect("e1", left_arm_ref.ports[self.arm.GAP_PORT_NAME], allow_layer_mismatch=True)
            gap.connect("e2", right_arm_ref.ports[self.arm.GAP_PORT_NAME], allow_layer_mismatch=True)

        # Add ports for the arms
        c.add_ports(right_arm_ref.ports, prefix=self.RIGHT_PREFIX)
        c.add_ports(left_arm_ref.ports, prefix=self.LEFT_PREFIX)

        return c

    def total_length(self) -> float:
        """
        Returns the total length of the junction.
        This method returns the total length of both arms plus the gap length.
        The total length is calculated as twice the arm length plus the gap length.
        """
        return self.arm.total_length() * 2 + self.gap_length
    
    def validate(self) -> None:
        if self.gap_length <= 0:
            raise ValueError("Gap length must be positive.")
        
        self.arm.validate()