from copy import copy
from dataclasses import dataclass, field
from typing import TypeAlias

from .component import ComponentData
from .enums import ComponentType, InternalEdgeRole
from .internals import InternalEdge, Port
import numpy as np

ValvePortRow: TypeAlias = tuple[int | None, ...]
ValvePortLayout: TypeAlias = list[ValvePortRow]

DEFAULT_STATOR_PORTS: ValvePortLayout = [(1, 2, 3, 4, 5, 6), (0,)]
DEFAULT_ROTOR_PORTS: ValvePortLayout = [(7, None, None, None, None, None), (7,)]


def _copy_port_layout(layout: ValvePortLayout) -> ValvePortLayout:
    return [tuple(row) for row in layout]


def rotate_rotor(
    rotor_ports: ValvePortLayout, clockwise: bool = True
) -> ValvePortLayout:
    rotor_ports_new = [(), rotor_ports[1]]
    if clockwise:
        rotor_ports_new[0] = (rotor_ports[0][-1],) + rotor_ports[0][:-1]
    else:
        rotor_ports_new[0] = rotor_ports[0][1:] + (rotor_ports[0][0],)
    return rotor_ports_new


def connection_from_rotor(
    stator_ports: ValvePortLayout,
    rotor_ports: ValvePortLayout,
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    rotor_position: list[tuple[int, int]] = []
    connection: list[tuple[int, int]] = []
    rotor_variable = [element for element in rotor_ports[0]]

    for i, element in enumerate(rotor_variable):
        if element is None:
            continue

        for j, partner in enumerate(rotor_variable):
            if partner == element and j != i:
                rotor_variable[j] = None
                rotor_variable[i] = None
                rotor_position.append((i + 1, j + 1))

                origin_port = stator_ports[0][i]
                destination_port = stator_ports[0][j]
                if origin_port is not None and destination_port is not None:
                    connection.append((origin_port, destination_port))

                break

    rotor_variable = [element for element in rotor_ports[0]]
    if rotor_ports[1][0] is not None:
        for j, partner in enumerate(rotor_variable):
            if partner == rotor_ports[1][0]:
                rotor_position.append((0, j + 1))
                destination_port = stator_ports[0][j]
                if destination_port is not None:
                    connection.append((0, destination_port))
                break

    return rotor_position, connection


def possibles_connections_pairs(
    stator_ports: ValvePortLayout,
    rotor_ports: ValvePortLayout,
) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    rotor_new = copy(rotor_ports)

    for _ in range(len(rotor_ports[0])):
        rotor_new = rotate_rotor(rotor_ports=rotor_new)
        _, connections = connection_from_rotor(
            stator_ports=stator_ports,
            rotor_ports=rotor_new,
        )
        points.extend(connections)

    return sorted(set(points))


def _port_numbers_from_stator(stator_ports: ValvePortLayout) -> list[int]:
    numbers = {
        number
        for row in stator_ports
        for number in row
        if number is not None
    }
    return sorted(numbers)


@dataclass
class ValveComponentData(ComponentData):
    COMPONENT_TYPE = ComponentType.UTENSIL
    # Internally properties (It will be overwritten according to the valve topology)
    stator_ports: ValvePortLayout = field(
        default_factory=lambda: _copy_port_layout(DEFAULT_STATOR_PORTS)
    )
    rotor_ports: ValvePortLayout = field(
        default_factory=lambda: _copy_port_layout(DEFAULT_ROTOR_PORTS)
    )
    internal_radius = 1

    def internal_structure(self, update: bool = False):
        if update:
            self.port_pairs.clear()
            self.ports_by_number.clear()
            self.internal_edges.clear()

        connections = possibles_connections_pairs(
            stator_ports=self.stator_ports,
            rotor_ports=self.rotor_ports,
        )
        valve_port_pairs: list[tuple[int, ...]] = [pair for pair in connections]
        self.port_pairs = valve_port_pairs
        self.ports_by_number = {
            number: Port(number=number, component=self.name)
            for number in _port_numbers_from_stator(self.stator_ports)
        }
        self.internal_edges = {
            pair: InternalEdge(
                origin_port=pair[0],
                destination_port=pair[1],
                role=InternalEdgeRole.JUNCTION,
                active=False,
            )
            for pair in connections
        }

        _, active_connections = connection_from_rotor(
            stator_ports=self.stator_ports,
            rotor_ports=self.rotor_ports,
        )
        for pair in active_connections:
            self.internal_edges[pair].active = True

        # Correct of the position of the ports
        n = len(self.stator_ports[0])
        angles_effective = np.arange(-np.pi / 2, 3 * np.pi / 2, 2 * np.pi / n)
        for i, c in enumerate(self.stator_ports[0]):
            if c is not None:
                phi = angles_effective[i]
                self.ports_by_number[c].relative_position = (
                    self.internal_radius * np.cos(phi),
                    self.internal_radius * np.sin(phi),
                )