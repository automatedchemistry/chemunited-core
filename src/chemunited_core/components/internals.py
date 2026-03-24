from dataclasses import dataclass
from ..common.enums import ConnectionType
from ..connections import EdgeData
from ..utils.internal_qunatity import ChemUnitQuantity


@dataclass
class Port:
    number: int
    component: str
    category: ConnectionType = ConnectionType.FLOW
    relative_position: tuple[float, float] = (0, 0)

    @property
    def name(self):
        return f"{self.component}.{self.number}"
    

@dataclass
class InternalEdge(EdgeData):
    classification = ConnectionType.FLOW
    origin="INTERNAL"
    destination="INTERNAL"
    origin_port=1
    destination_port=2
    length = ChemUnitQuantity("1 mm")
    diameter = ChemUnitQuantity("1 mm")
