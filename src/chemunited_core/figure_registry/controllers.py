from dataclasses import dataclass

from typing_extensions import override

from chemunited_core.components import MassFlowControllerData, PutResult
from chemunited_core.utils.internal_quantity import ChemUnitQuantity


@dataclass
class MFCComponentData(MassFlowControllerData):

    @override
    def apply(self, command: str, **kwargs) -> PutResult:
        if command == "set-flow-rate":
            self.flowrate = ChemUnitQuantity(kwargs["flowrate"])
            if self.flowrate_si <= 0.0:
                self.internal_edges[(1, 2)].close()
        return PutResult()
