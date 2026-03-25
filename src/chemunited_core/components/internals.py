from dataclasses import dataclass
from ..common.enums import ConnectionType
from ..connections import EdgeData
from ..utils.internal_quantity import ChemUnitQuantity


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
    classification: ConnectionType = ConnectionType.FLOW
    origin: str = "INTERNAL"
    destination: str = "INTERNAL"
    origin_port: int = 1
    destination_port: int = 2
    length: ChemUnitQuantity = ChemUnitQuantity("1 mm")
    diameter: ChemUnitQuantity = ChemUnitQuantity("1 mm")


@dataclass
class Inventory(Port):
    volume: float = 1e-6
    

