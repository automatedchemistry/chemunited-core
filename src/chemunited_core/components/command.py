"""Command effect — the contract between ComponentData and the simulation server.

When a component receives a command via ``receive_command``, it updates its own
internal state and returns a ``CommandEffect`` describing what the simulation
graph must update in response.

Two propagation patterns exist in the sim:

- **Shared-reference** (e.g. ``FlowSourceData``): ``sync_internal_state()`` mutates
  ``PortBoundaryCondition.value`` in-place. Because the compiled ``HydraulicNode``
  holds a reference to the same object, the solver picks up the change automatically
  on the next step. Return an empty ``CommandEffect()``.

- **Value-copy** (e.g. ``ValveComponentData``): ``HydraulicEdge.resistance_override``
  is a primitive copied at compile time, so the sim server must bridge
  ``InternalEdge.resistance_override`` → ``HydraulicEdge.resistance_override``
  explicitly. Populate ``edge_overrides`` to signal this.

The server in ``chemunited-sim`` reads ``CommandEffect`` and applies any
necessary graph updates while holding the simulation lock, ensuring the
change lands atomically between two ``Worker.step()`` calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CommandEffect:
    """Describes what the simulation graph must update after a ``receive_command`` call.

    An empty ``CommandEffect`` means propagation was already handled by
    ``sync_internal_state()`` via shared object references — the server does nothing
    extra.

    A non-empty ``CommandEffect`` carries explicit instructions for the server to
    apply graph-level patches while holding the simulation step lock.

    Attributes
    ----------
    edge_overrides:
        Valve-type bridge data. Maps ``(origin_port, dest_port)`` to the new
        ``resistance_override`` value (``None`` = open, ``R_MAX_HYDRAULIC`` = closed).
        The server translates port pairs to ``HydraulicEdge`` IDs using the component
        name: ``f"{comp_name}.{origin}.{dest}"``.
    """

    edge_overrides: dict[tuple[int, int], float | None] = field(default_factory=dict)