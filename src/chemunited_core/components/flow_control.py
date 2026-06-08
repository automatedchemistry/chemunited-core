"""Inline flow-control components: Pump and MassFlowController.

Both use a hub-at-port-1 + junction-edge topology so upstream transport
pockets are staged and re-emitted rather than discarded.

Pump         — forces exactly Q from port 1 to port 2 via a Neumann BC at
               port 2. When Q=0 the junction edge is closed, blocking passive flow.

MassFlowController — allows flow up to a setpoint by varying the junction-edge
               resistance each hydraulic step. When setpoint=0 the edge is
               fully closed.
"""

from dataclasses import dataclass
from typing import Annotated, ClassVar

from pydantic import Field
from typing_extensions import override

from chemunited_core.common.enums import GroupParameterCategory
from chemunited_core.utils.internal_quantity import (
    ChemQuantityValidator,
    ChemUnitQuantity,
)

from .component import ComponentData, ComponentMode
from .enums import BoundaryConditionKind, ComponentType, InternalEdgeRole
from .internals import InternalEdge, Port, PortBoundaryCondition

# ---------------------------------------------------------------------------
# Pump
# ---------------------------------------------------------------------------


class PumpMode(ComponentMode):
    flow_rate: Annotated[ChemUnitQuantity, ChemQuantityValidator("ml/min")] = Field(
        default=ChemUnitQuantity("0 ml/min"),
        title="Flow Rate",
        description="Volumetric flow rate the pump forces through the network.",
        json_schema_extra={
            "group": GroupParameterCategory.STATUS.value,
        },
    )


@dataclass
class PumpData(ComponentData):
    """Two-port inline pump: hub at port 1, Neumann BC at port 2.

    When flow_rate > 0 the junction edge is open and port 2 imposes +Q.
    When flow_rate = 0 the edge is closed — no passive flow is allowed.
    """

    COMPONENT_TYPE: ClassVar[ComponentType] = ComponentType.ELECTRONIC
    flow_rate: ChemUnitQuantity = ChemUnitQuantity("0 ml/min")

    @property
    def flow_rate_si(self) -> float:
        return float(self.flow_rate.to_base_units().magnitude)  # m³/s

    @override
    def internal_structure(self) -> None:
        self.port_pairs = [(1, 2)]
        self.ports_by_number = {
            1: Port(number=1, component=self.name, is_hub=True),
            2: Port(
                number=2,
                component=self.name,
                boundary=PortBoundaryCondition(
                    kind=BoundaryConditionKind.FLOW, value=0.0
                ),
            ),
        }
        self.internal_edges = {
            (1, 2): InternalEdge(
                origin_port=1,
                destination_port=2,
                role=InternalEdgeRole.JUNCTION,
            ).close()
        }
        self.internal_inventories = {}

    def _sync(self) -> None:
        boundary = self.ports_by_number[2].boundary
        if boundary is None:
            raise RuntimeError("Pump port 2 must define a flow boundary.")

        if self.flow_rate_si > 0:
            self.internal_edges[(1, 2)].open()
            boundary.value = self.flow_rate_si
        else:
            self.internal_edges[(1, 2)].close()
            boundary.value = 0.0

    @override
    def sync_internal_state(self) -> None:
        self._sync()


# ---------------------------------------------------------------------------
# MassFlowController
# ---------------------------------------------------------------------------


class MassFlowControllerMode(ComponentMode):
    setpoint: Annotated[ChemUnitQuantity, ChemQuantityValidator("ml/min")] = Field(
        default=ChemUnitQuantity("0 ml/min"),
        title="Flow Setpoint",
        description="Maximum volumetric flow rate the MFC allows through.",
        json_schema_extra={
            "group": GroupParameterCategory.STATUS.value,
        },
    )


@dataclass
class MassFlowControllerData(ComponentData):
    """Two-port inline mass-flow controller: hub at port 1, variable resistance.

    The junction-edge resistance is adjusted each hydraulic step by the sim
    worker (via update_resistance) so that flow does not exceed setpoint.
    When setpoint=0 the edge is fully closed.
    """

    COMPONENT_TYPE: ClassVar[ComponentType] = ComponentType.ELECTRONIC
    setpoint: ChemUnitQuantity = ChemUnitQuantity("0 ml/min")

    @property
    def setpoint_si(self) -> float:
        return float(self.setpoint.to_base_units().magnitude)  # m³/s

    @override
    def internal_structure(self) -> None:
        self.port_pairs = [(1, 2)]
        self.ports_by_number = {
            1: Port(number=1, component=self.name, is_hub=True),
            2: Port(number=2, component=self.name),
        }
        edge = InternalEdge(
            origin_port=1,
            destination_port=2,
            role=InternalEdgeRole.JUNCTION,
        )
        if self.setpoint_si <= 0.0:
            edge.close()
        self.internal_edges = {(1, 2): edge}
        self.internal_inventories = {}

    def update_resistance(self, dp: float) -> None:
        """Update the junction-edge resistance from the last hydraulic solve.

        Called once per tick by the sim worker with dp = P_port1 - P_port2.
        Closes on dp ≤ 0 to block reverse flow (one-way device).
        """
        if self.setpoint_si <= 0.0 or dp <= 0.0:
            self.internal_edges[(1, 2)].close()
        else:
            r = dp / self.setpoint_si
            self.internal_edges[(1, 2)].open()
            self.internal_edges[(1, 2)].resistance_override = max(r, 0.0) or None
