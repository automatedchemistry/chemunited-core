from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

from chemunited_core.common.enums import ConnectionType
from chemunited_core.components import ComponentData
from chemunited_core.connections import EdgeData, EdgeMode
from chemunited_core.figure_registry import COMPONENTS


@dataclass
class RegistryGraph:
    components: list[ComponentData]
    connections: list[EdgeData]


def _build_component(figure: str, index: int) -> ComponentData:
    data_class, mode_class = COMPONENTS[figure]
    mode = mode_class(
        name=figure,
        figure=figure,
        position=(float(index), 0.0),
        angle=0,
    )
    return data_class.from_mode(mode)


def _first_visible_ports_by_category(
    component: ComponentData,
) -> dict[ConnectionType, int]:
    ports_by_category: dict[ConnectionType, int] = {}

    for port_number, port in sorted(component.ports_by_number.items()):
        if port.show_in_graph:
            ports_by_category.setdefault(port.category, port_number)

    return ports_by_category


def build_registry_graph() -> RegistryGraph:
    components = [
        _build_component(figure, index)
        for index, figure in enumerate(COMPONENTS, start=1)
    ]
    ports_by_category: dict[ConnectionType, list[tuple[ComponentData, int]]] = {}

    for component in components:
        for category, port_number in _first_visible_ports_by_category(
            component
        ).items():
            ports_by_category.setdefault(category, []).append((component, port_number))

    connections: list[EdgeData] = []
    for category, endpoints in ports_by_category.items():
        for (origin, origin_port), (destination, destination_port) in pairwise(
            endpoints
        ):
            connections.append(
                EdgeData.from_mode(
                    EdgeMode(
                        origin=origin.name,
                        destination=destination.name,
                        origin_port=origin_port,
                        destination_port=destination_port,
                        classification=category,
                        length="100 mm",
                        diameter="1 mm",
                    )
                )
            )

    return RegistryGraph(components=components, connections=connections)


def test_figure_registry_components_build_graph() -> None:
    graph = build_registry_graph()
    component_index = {component.name: component for component in graph.components}

    assert set(component_index) == set(COMPONENTS)
    assert len(graph.components) == len(COMPONENTS)
    assert graph.connections

    for component in graph.components:
        assert component.figure == component.name
        for port_number, port in component.ports_by_number.items():
            assert port.number == port_number
            assert port.component == component.name
        for (origin, destination), internal_edge in component.internal_edges.items():
            assert internal_edge.origin_port == origin
            assert internal_edge.destination_port == destination

    for connection in graph.connections:
        origin = component_index[connection.origin]
        destination = component_index[connection.destination]

        assert connection.origin_port in origin.ports_by_number
        assert connection.destination_port in destination.ports_by_number
        assert (
            origin.ports_by_number[connection.origin_port].category
            == connection.classification
        )
        assert (
            destination.ports_by_number[connection.destination_port].category
            == connection.classification
        )


def test_solenoid_valve_2_way_common_port_is_hub() -> None:
    data_class, mode_class = COMPONENTS["SolenoidValve2Way"]
    component = data_class.from_mode(mode_class(name="divertvalve"))

    assert sorted(component.ports_by_number) == [0, 1, 2]
    assert component.ports_by_number[0].is_hub is True
    assert component.ports_by_number[1].is_hub is False
    assert component.ports_by_number[2].is_hub is False
    assert set(component.internal_edges) == {(0, 1), (0, 2)}
