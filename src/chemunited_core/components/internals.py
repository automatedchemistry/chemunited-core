from dataclasses import dataclass, field

from chemunited_core.common.enums import ConnectionType
from chemunited_core.compounds import VolumeContentBase

from .enums import InternalEdgeRole, PortAccess, PortClosure


@dataclass
class Port:
    number: int
    component: str
    category: ConnectionType = ConnectionType.FLOW
    relative_position: tuple[float, float] = (0, 0)
    access: PortAccess = PortAccess.TOP
    closure: PortClosure = PortClosure.OPEN  # physical user configuration only

    @property
    def name(self):
        return f"{self.component}.{self.number}"

    def block(self, value: bool = True):
        self.closure = PortClosure.CAPPED if value else PortClosure.OPEN


@dataclass
class InternalEdge:
    """Internal channel connecting two ports within a component subgraph.
    All physical quantities in SI units."""

    origin_port: int = 1
    destination_port: int | str = 2
    length: float = 1e-3
    diameter: float = 1e-3
    role: InternalEdgeRole = InternalEdgeRole.TRANSPORT
    active: bool = True  # ← switching control


@dataclass
class InventoryNode:
    """Lumped control volume inside a component subgraph.
    Accepts parcels of any phase and tracks inventory per phase internally.
    All physical quantities in SI units."""

    # Default vessel inventory starts with one gas phase and one liquid phase.
    liq_content: VolumeContentBase = field(default_factory=VolumeContentBase)
    gas_content: VolumeContentBase = field(default_factory=VolumeContentBase)
