# chemunited-core

> Core data models for orchestration, execution, and simulation of protocols in automated chemistry laboratory platforms.

`chemunited-core` is the foundational layer upon which upper-level orchestration, execution, and simulation packages are built. It defines the canonical data structures for process equipment, connections, and physical quantities used across the ChemUnited ecosystem.

---

## Installation

Requires Python ≥ 3.11.

```bash
pip install chemunited-core
```

For development (includes `pytest`, `pytest-cov`, `black`, `ruff`, `mypy`, and `pre-commit`):

```bash
pip install -e ".[dev]"
```

---

## Architecture

The library uses a consistent **two-layer pattern** throughout:

```
Pydantic model (*Mode)  →  from_mode()  →  Dataclass (*Data)
     validation                bridge          runtime data
```

- **`*Mode` classes** — Pydantic models that validate and parse user input.
- **`*Data` classes** — Python dataclasses used at runtime, constructed via the `from_mode()` factory.
- **`Element.from_mode(mode)`** — the bridge method inherited by every `*Data` class. It validates that all required fields are present in the model before constructing the dataclass.

---

## Modules

### `chemunited_core.components`

Process equipment definitions.

| Class | Type | Description |
|---|---|---|
| `ComponentMode` | Pydantic model | Base component input model (name, figure, position, angle) |
| `ComponentData` | Dataclass | Base runtime component; 1 port pair `(1, 2)` by default |
| `NeutralComponentData` | Dataclass | Component variant that skips port initialization |
| `VesselMode` | Pydantic model | Vessel input model (capacity, top/bottom access ports) |
| `VesselComponentData` | Dataclass | Vessel with volumetric capacity; n+1 ports (top + bottom + 1 heat port) |
| `PlugFlowMode` | Pydantic model | Tubular reactor input model (length, diameter) |
| `PlugFlowComponentData` | Dataclass | Plug-flow reactor; capacity calculated as `length × π × diameter² / 4` |

### `chemunited_core.connections`

Directed edges between component ports.

| Class | Type | Description |
|---|---|---|
| `EdgeMode` | Pydantic model | Connection input model with origin/destination ports and physical geometry |
| `EdgeData` | Dataclass | Runtime connection; carries `classification`, `length`, `diameter`, `capacity` |

**Constraint**: non-`FLOW` connections (`MOVEMENT`, `HEAT`, `ELECTRONIC`) automatically enforce `length = 0 mm` and `diameter = 0 mm`.

**Field aliasing**: `EdgeMode` accepts `destiny` as an alias for `destination` and `destiny_port` as an alias for `destination_port`.

### `chemunited_core.common`

Shared enums and the base class.

```python
class ConnectionType(StrEnum):
    FLOW       = "flow"
    MOVEMENT   = "movement"
    HEAT       = "heat"
    ELECTRONIC = "electronic"

class GroupParameterCategory(StrEnum):
    GENERAL  = "General"
    PROPERTY = "Property"
    STATUS   = "Status"
```

### `chemunited_core.utils`

Unit-aware physical quantities via [Pint](https://pint.readthedocs.io/).

| Name | Description |
|---|---|
| `ChemUnitQuantity` | Custom `Quantity` subclass with arithmetic and unit preservation |
| `ChemQuantityValidator` | Pydantic validator wrapper for `ChemUnitQuantity` fields |
| `ureg` | Shared `UnitRegistry` instance — always use this for unit operations |

---

## Usage

### Creating a component

```python
from chemunited_core.components import ComponentMode, ComponentData

mode = ComponentMode(name="Pump A", figure="PumpFigure", position=(0.0, 0.0), angle=0)
component = ComponentData.from_mode(mode)

print(component.port_pairs)       # [(1, 2)]
print(component.ports_by_number)  # {1: Port(...), 2: Port(...)}
```

### Creating a vessel

```python
from chemunited_core.components import VesselMode, VesselComponentData

mode = VesselMode(
    name="Flask1",
    figure="FlaskFigure",
    position=(1.0, 0.0),
    angle=0,
    capacity="250 ml",
    top_access=3,
    bottom_access=2,
)
vessel = VesselComponentData.from_mode(mode)
print(vessel.capacity)  # 250 ml
```

### Creating a plug-flow reactor

```python
from chemunited_core.components import PlugFlowMode, PlugFlowComponentData

mode = PlugFlowMode(
    name="Reactor1",
    figure="TubeFigure",
    position=(2.0, 0.0),
    angle=0,
    length="500 mm",
    diameter="2 mm",
)
reactor = PlugFlowComponentData.from_mode(mode)
print(reactor.capacity)  # volume in m³
```

### Creating a connection

```python
from chemunited_core.connections import EdgeMode, EdgeData

mode = EdgeMode(
    origin="Pump A",
    destination="Flask1",
    origin_port=2,
    destination_port=1,
    length="150 mm",
    diameter="1 mm",
)
edge = EdgeData.from_mode(mode)
print(edge.name)      # "Pump A_2_Flask1_1"
print(edge.capacity)  # cross-sectional volume in m³
```

---

## Development

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run a single test file
pytest tests/test_from_mode.py
```

Pre-commit hooks (Ruff lint/import sorting, Black formatting, mypy, and general checks) are configured in `.pre-commit-config.yaml`:

```bash
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `pydantic` | ≥ 2.0 | Input validation and schema definition |
| `pint` | ≥ 0.23 | Physical unit handling |
| `pydantic-pint` | ≥ 0.3 | Pydantic integration for Pint quantities |
| `numpy` | ≥ 1.26 | Numerical operations |

---

## License

See [LICENSE](LICENSE) for details.

---

## Author

Samuel Vitor Saraiva — Max Planck Institute of Colloids and Interfaces
