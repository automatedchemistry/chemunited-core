from chemunited_core.common.enums import PhaseKind
from chemunited_core.common.constant import ATMOSPHERE_PRESSURE_PA, AMBIENT_TEMPERATURE_K
from dataclasses import dataclass, field


@dataclass(slots=True)
class Pocket:
    """A discrete volume of matter in a single phase state.

    Represents a well-mixed region holding a chemical mixture at uniform
    pressure and temperature, tracking species amounts in moles.

    Attributes:
        phase_kind: Thermodynamic phase of the contents (e.g. liquid, gas).
        volume: Volume of the pocket in cubic metres.
        species_moles: Mapping of species identifier to amount in moles.
        pressure: Absolute pressure in Pascals (default: 1 atm).
        temperature: Temperature in Kelvin (default: 298.15 K).
        origin: Label identifying where this pocket was created.
        created_at: Simulation timestamp (s) at which the pocket was created.
    """

    phase_kind: PhaseKind
    volume: float
    species_moles: dict[str, float] = field(default_factory=dict)
    pressure: float = ATMOSPHERE_PRESSURE_PA
    temperature: float = AMBIENT_TEMPERATURE_K
    origin: str = "unknown"
    created_at: float = 0.0
