import gdsfactory as gf
from .base_junction import BaseJunctionConfig
from .base_arm import BaseArmConfig
from .regular_arm import RegularArmConfig
class SymmetricJunctionConfig(BaseJunctionConfig):
    """
    Base configuration for symmetric junction components.
    Attributes:
        arm (BaseArmConfig): Configuration for the arm component.
        gap_length (float): Length of the gap between the arms.
        layer (LayerSpec): Layer specification for the junction component.
    """
        
    arm: BaseArmConfig = RegularArmConfig()

    def build(self) -> gf.Component:
        c = gf.Component()
        
        # Create left and right arms using the same arm configuration
        a = self.arm.build()       

        right_arm_ref = c << a.copy()
        left_arm_ref = c << a.mirror_x()

        # Add validation that port "gap" exists in both arms

        # Connect the arms via ports
        left_arm_ref.connect("gap", right_arm_ref.ports["gap"])
        # Position the right arm
        left_arm_ref.movex(-self.gap_length)

        # Add ports for the arms
        c.add_ports(right_arm_ref.ports, prefix="right_")
        c.add_ports(left_arm_ref.ports, prefix="left_")

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