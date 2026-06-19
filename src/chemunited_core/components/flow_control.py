"""Inline flow-control components: Pump and MassFlowController.

Both use a hub-at-port-1 + junction-edge topology so upstream transport
pockets are staged and re-emitted rather than discarded.

Pump         — forces exactly Q from port 1 to port 2 by setting the junction
               resistance to R=dp/Q each tick (negative when working against
               back-pressure). When Q=0 the junction is fully closed.

MassFlowController — allows flow up to a setpoint by varying the junction-edge
               resistance each hydraulic step. When setpoint=0 the edge is
               fully closed.
"""

from dataclasses import dataclass
from typing import Annotated, ClassVar

from chemunited_quantities import (
    ChemQuantityValidator,
    ChemUnitQuantity,
)
from pydantic import Field
from typing_extensions import override

from chemunited_core.common.enums import GroupParameterCategory

from .component import ComponentData, ComponentMode
from .enums import ComponentType, InternalEdgeRole
from .internals import InternalEdge, Port

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
    """Two-port inline pump: hub at port 1, active-resistance junction.

    The junction resistance is set each tick by update_resistance(dp) so that
    exactly flow_rate passes from port 1 to port 2.  When the pump works
    against back-pressure dp < 0 the resistance is negative — correct for an
    active positive-displacement element.  When flow_rate = 0 the junction is
    fully closed.  No Neumann BC is used; transport pockets flow through the
    junction edge from the upstream hub to the downstream network.
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
            2: Port(number=2, component=self.name),
        }
        self.internal_edges = {
            (1, 2): InternalEdge(
                origin_port=1,
                destination_port=2,
                role=InternalEdgeRole.JUNCTION,
            ).close()
        }
        self.internal_inventories = {}

    def update_resistance(self, dp: float) -> None:
        """Set junction resistance so exactly flow_rate passes port 1→2.

        Called once per tick by the sim worker with dp = P_port1 − P_port2.
        R = dp / Q is negative when the pump works against back-pressure,
        which correctly models an active positive-displacement element.
        """
        if self.flow_rate_si <= 0.0:
            self.internal_edges[(1, 2)].close()
            return
        r = dp / self.flow_rate_si
        self.internal_edges[(1, 2)].open()
        self.internal_edges[(1, 2)].resistance_override = r if r != 0.0 else None

    def _sync(self) -> None:
        if self.flow_rate_si <= 0.0:
            self.internal_edges[(1, 2)].close()

    @override
    def sync_internal_state(self) -> None:
        self._sync()


# ---------------------------------------------------------------------------
# MassFlowController
# ---------------------------------------------------------------------------


class MassFlowControllerMode(ComponentMode):
    flowrate: Annotated[ChemUnitQuantity, ChemQuantityValidator("ml/min")] = Field(
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
    When flowrate=0 the edge is fully closed.
    """

    COMPONENT_TYPE: ClassVar[ComponentType] = ComponentType.ELECTRONIC
    flowrate: ChemUnitQuantity = ChemUnitQuantity("0 ml/min")

    @property
    def flowrate_si(self) -> float:
        return float(self.flowrate.to_base_units().magnitude)  # m³/s

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
        if self.flowrate_si <= 0.0:
            edge.close()
        self.internal_edges = {(1, 2): edge}
        self.internal_inventories = {}

    def update_resistance(self, dp: float) -> None:
        """Update the junction-edge resistance from the last hydraulic solve.

        Called once per tick by the sim worker with dp = P_port1 - P_port2.
        Closes on dp ≤ 0 to block reverse flow (one-way device).
        """
        if self.flowrate_si <= 0.0 or dp <= 0.0:
            self.internal_edges[(1, 2)].close()
        else:
            r = dp / self.flowrate_si
            self.internal_edges[(1, 2)].open()
            self.internal_edges[(1, 2)].resistance_override = max(r, 0.0) or None
