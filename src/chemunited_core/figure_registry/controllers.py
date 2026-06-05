from chemunited_core.components import PutResult, MassFlowControllerData
from chemunited_core.utils.internal_quantity import ChemUnitQuantity
from typing_extensions import override
from dataclasses import dataclass


@dataclass
class MFCComponentData(MassFlowControllerData):

    @override
    def apply(self, command: str, **kwargs) -> PutResult:
        if command == "set":
            self.setpoint = ChemUnitQuantity(kwargs["setpoint"])
            if self.setpoint_si <= 0.0:
                self.internal_edges[(1, 2)].close()
        return PutResult()
