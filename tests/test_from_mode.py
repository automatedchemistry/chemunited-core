import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from chemunited_core.common.metadata import Element
from chemunited_core.components.component import ComponentData
from chemunited_core.components.vessel import VesselComponentData, VesselMode
from chemunited_core.connections.enums import ConnectionType
from chemunited_core.connections.edge import EdgeData, EdgeMode


class ExtraEdgeMode(EdgeMode):
    extra_label: str = "ignored"


class MissingLengthMode(BaseModel):
    origin: str = "reactor"
    destination: str = "collector"
    origin_port: int = 1
    destination_port: int = 2
    classification: ConnectionType = ConnectionType.FLOW
    diameter: str = "3 mm"
    straight_path: bool = True
    air_pressure_line: bool = False


class MinimalMode(BaseModel):
    name: str = "pump"


@dataclass
class OptionalElement(Element):
    name: str
    enabled: bool = True


@dataclass
class StrictElement(Element):
    name: str
    enabled: bool


class TestFromMode(unittest.TestCase):
    def test_component_data_initializes_default_ports(self) -> None:
        component = ComponentData(
            name="pump",
            figure="PumpFigure",
            position=(0.0, 0.0),
            angle=90,
        )

        self.assertEqual(component.port_pairs, [(1, 2)])
        self.assertEqual(component.port_numbers, [1, 2])
        self.assertEqual(set(component.ports_by_number), {1, 2})
        self.assertEqual(component.ports_by_number[1].name, "pump.1")

    def test_component_data_legacy_port_aliases_share_state(self) -> None:
        component = ComponentData(
            name="pump",
            figure="PumpFigure",
            position=(0.0, 0.0),
            angle=90,
        )

        self.assertIs(component.ports_pairs, component.port_pairs)
        self.assertIs(component.ports_class, component.ports_by_number)

    def test_edge_data_from_mode_preserves_runtime_types(self) -> None:
        mode = EdgeMode()

        edge = EdgeData.from_mode(mode)

        self.assertIsInstance(edge, EdgeData)
        self.assertEqual(edge.origin, mode.origin)
        self.assertEqual(edge.destination, mode.destination)
        self.assertIs(edge.classification, mode.classification)
        self.assertEqual(type(edge.length), type(mode.length))
        self.assertEqual(type(edge.diameter), type(mode.diameter))
        self.assertEqual(edge.length, mode.length)
        self.assertEqual(edge.diameter, mode.diameter)

    def test_edge_data_from_mode_keeps_normalized_non_flow_values(self) -> None:
        mode = EdgeMode(
            classification=ConnectionType.HEAT,
            length="25 mm",
            diameter="2 mm",
            air_pressure_line=True,
        )

        edge = EdgeData.from_mode(mode)

        self.assertEqual(edge.classification, ConnectionType.HEAT)
        self.assertEqual(str(edge.length), "0 millimeter")
        self.assertEqual(str(edge.diameter), "0 millimeter")
        self.assertTrue(edge.air_pressure_line)

    def test_extra_mode_fields_are_ignored(self) -> None:
        edge = EdgeData.from_mode(ExtraEdgeMode(extra_label="side-channel"))

        self.assertIsInstance(edge, EdgeData)
        self.assertFalse(hasattr(edge, "extra_label"))

    def test_legacy_destination_aliases_are_still_accepted(self) -> None:
        mode = EdgeMode(destiny="collector", destiny_port=2)
        edge = EdgeData.from_mode(mode)

        self.assertEqual(mode.destination, "collector")
        self.assertEqual(mode.destiny, "collector")
        self.assertEqual(edge.destination, "collector")
        self.assertEqual(edge.destiny, "collector")
        self.assertEqual(edge.destination_port, 2)
        self.assertEqual(edge.destiny_port, 2)

    def test_edge_data_value_properties_read_from_dataclass_fields(self) -> None:
        edge = EdgeData.from_mode(EdgeMode(length="25 mm", diameter="2 mm"))

        self.assertEqual(edge.length_value, edge.length.to_base_units().magnitude)
        self.assertEqual(
            edge.diameter_value, edge.diameter.to_base_units().magnitude
        )

    def test_non_flow_validation_does_not_mutate_schema_metadata(self) -> None:
        schema_before = EdgeMode.model_json_schema()

        EdgeMode(classification=ConnectionType.HEAT)

        schema_after = EdgeMode.model_json_schema()

        self.assertEqual(
            schema_before["properties"]["length"].get("visible"),
            schema_after["properties"]["length"].get("visible"),
        )
        self.assertEqual(
            schema_before["properties"]["diameter"].get("visible"),
            schema_after["properties"]["diameter"].get("visible"),
        )

    def test_dataclass_defaults_are_used_when_mode_field_is_missing(self) -> None:
        element = OptionalElement.from_mode(MinimalMode())

        self.assertEqual(element.name, "pump")
        self.assertTrue(element.enabled)

    def test_vessel_component_data_from_mode_requires_vessel_mode(self) -> None:
        vessel = VesselComponentData.from_mode(VesselMode(name="reactor"))

        self.assertIsInstance(vessel, VesselComponentData)
        self.assertEqual(vessel.name, "reactor")

        with self.assertRaisesRegex(
            TypeError,
            r"VesselComponentData\.from_mode expects VesselMode, got MinimalMode\.",
        ):
            VesselComponentData.from_mode(MinimalMode())

    def test_missing_required_field_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(
            TypeError,
            r"Cannot build EdgeData from MissingLengthMode: missing required field\(s\) 'length'\.",
        ):
            EdgeData.from_mode(MissingLengthMode())

        with self.assertRaisesRegex(
            TypeError,
            r"Cannot build StrictElement from MinimalMode: missing required field\(s\) 'enabled'\.",
        ):
            StrictElement.from_mode(MinimalMode())

if __name__ == "__main__":
    unittest.main()
