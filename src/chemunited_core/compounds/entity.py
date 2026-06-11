"""Chemical entity definition for the chemunited-core compounds module.

Defines ChemicalEntity, a static descriptor for a pure chemical substance.
Stores user-provided physical properties and provides derived quantities
computed on demand using simplified ideal-gas and ideal-mixture assumptions.

Used by:
    - GUI (Setup Manager) to populate compound pickers and validate species names.
    - chemunited-sim to retrieve Cp, density, and molar volume during heat balance
      and pocket property calculations.
"""

from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from chemunited_core.common.enums import GroupParameterCategory
from chemunited_core.utils.internal_quantity import (
    ChemQuantityValidator,
    ChemUnitQuantity,
)

IDEAL_GAS_CONSTANT = 8.314  # J/(mol*K)


def _quantity_with_default_unit(value: object, unit: str) -> object:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return ChemUnitQuantity(value, unit)
    return value


class ChemicalEntity(BaseModel):
    """Static descriptor for a pure chemical substance."""

    name: Annotated[
        str,
        Field(
            default="air",
            min_length=1,
            title="Name",
            description="Unique identifier used as the species key.",
            json_schema_extra={"group": GroupParameterCategory.GENERAL.value},
        ),
    ]
    molecular_weight: Annotated[
        ChemUnitQuantity,
        ChemQuantityValidator("g/mol"),
    ] = Field(
        default=ChemUnitQuantity("28.97 g/mol"),
        title="Molecular Weight",
        description="Molar mass of the pure chemical substance.",
        json_schema_extra={"group": GroupParameterCategory.PROPERTY.value},
    )
    cp_liquid: Annotated[
        ChemUnitQuantity,
        ChemQuantityValidator("J/(mol*K)"),
    ] = Field(
        default=ChemUnitQuantity("0 J/(mol*K)"),
        title="Liquid Heat Capacity",
        description=(
            "Molar heat capacity of the liquid phase. A value of zero means "
            "the liquid phase is not available."
        ),
        json_schema_extra={"group": GroupParameterCategory.PROPERTY.value},
    )
    cp_gas: Annotated[
        ChemUnitQuantity,
        ChemQuantityValidator("J/(mol*K)"),
    ] = Field(
        default=ChemUnitQuantity("29.1 J/(mol*K)"),
        title="Gas Heat Capacity",
        description=(
            "Molar heat capacity of the gas phase. A value of zero means "
            "the gas phase is not available."
        ),
        json_schema_extra={"group": GroupParameterCategory.PROPERTY.value},
    )
    density_liquid: Annotated[
        ChemUnitQuantity,
        ChemQuantityValidator("kg/m^3"),
    ] = Field(
        default=ChemUnitQuantity("0 kg/m^3"),
        title="Liquid Density",
        description=(
            "Density of the liquid phase. A value of zero means the liquid "
            "phase is not available."
        ),
        json_schema_extra={"group": GroupParameterCategory.PROPERTY.value},
    )
    color_red: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            le=255,
            title="Red",
            description="Red channel for GUI color visualization.",
            json_schema_extra={"group": "Design"},
        ),
    ]
    color_green: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            le=255,
            title="Green",
            description="Green channel for GUI color visualization.",
            json_schema_extra={"group": "Design"},
        ),
    ]
    color_blue: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            le=255,
            title="Blue",
            description="Blue channel for GUI color visualization.",
            json_schema_extra={"group": "Design"},
        ),
    ]
    color_alpha: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            le=255,
            title="Transparency",
            description=(
                "Alpha channel for GUI color visualization. A value of zero is "
                "fully transparent and 255 is fully opaque."
            ),
            json_schema_extra={"group": "Design"},
        ),
    ]

    @field_validator("molecular_weight", mode="before")
    @classmethod
    def coerce_molecular_weight(cls, value: object) -> object:
        return _quantity_with_default_unit(value, "g/mol")

    @field_validator("cp_liquid", "cp_gas", mode="before")
    @classmethod
    def coerce_heat_capacity(cls, value: object) -> object:
        return _quantity_with_default_unit(value, "J/(mol*K)")

    @field_validator("density_liquid", mode="before")
    @classmethod
    def coerce_density_liquid(cls, value: object) -> object:
        return _quantity_with_default_unit(value, "kg/m^3")

    @field_validator("molecular_weight")
    @classmethod
    def validate_molecular_weight(cls, value: ChemUnitQuantity) -> ChemUnitQuantity:
        if value <= ChemUnitQuantity("0 g/mol"):
            raise ValueError("molecular_weight must be greater than 0 g/mol.")
        return value

    @field_validator("cp_liquid", "cp_gas")
    @classmethod
    def validate_heat_capacity(cls, value: ChemUnitQuantity) -> ChemUnitQuantity:
        if value < ChemUnitQuantity("0 J/(mol*K)"):
            raise ValueError("heat capacity values must be greater than or equal to 0.")
        return value

    @field_validator("density_liquid")
    @classmethod
    def validate_density_liquid(cls, value: ChemUnitQuantity) -> ChemUnitQuantity:
        if value < ChemUnitQuantity("0 kg/m^3"):
            raise ValueError(
                "density_liquid must be greater than or equal to 0 kg/m^3."
            )
        return value

    @property
    def rgb_hex(self) -> str:
        """Return the editable RGB channels as a six-digit hex color."""
        return f"#{self.color_red:02X}{self.color_green:02X}{self.color_blue:02X}"

    @property
    def rgba_hex(self) -> str:
        """Return the editable RGBA channels as an eight-digit hex color."""
        return (
            f"#{self.color_red:02X}{self.color_green:02X}"
            f"{self.color_blue:02X}{self.color_alpha:02X}"
        )

    def molar_volume_gas(self, temperature: float, pressure: float) -> float:
        """Ideal-gas molar volume in m³/mol."""
        return IDEAL_GAS_CONSTANT * temperature / pressure

    def molar_volume_liquid(self) -> float:
        """Liquid molar volume in m³/mol derived from density."""
        if self.density_liquid <= ChemUnitQuantity("0 kg/m^3"):
            raise ValueError(
                f"density_liquid is not defined for compound '{self.name}'."
            )
        return float((self.molecular_weight / self.density_liquid).to("m^3/mol").magnitude)

    def cp(self, phase: str) -> float:
        """Molar heat capacity in J/(mol·K) for the requested phase."""
        if phase == "liquid":
            if self.cp_liquid <= ChemUnitQuantity("0 J/(mol*K)"):
                raise ValueError(
                    f"cp_liquid is not defined for compound '{self.name}'."
                )
            return float(self.cp_liquid.magnitude)
        if phase == "gas":
            if self.cp_gas <= ChemUnitQuantity("0 J/(mol*K)"):
                raise ValueError(f"cp_gas is not defined for compound '{self.name}'.")
            return float(self.cp_gas.magnitude)
        raise ValueError(f"Unknown phase '{phase}'. Expected 'liquid' or 'gas'.")
