from dataclasses import dataclass
from typing import Annotated
from pydantic import Field

from ..common.enums import GroupParameterCategory, ConnectionType
from ..utils.quantity import ChemQuantityValidator, ChemUnitQuantity
from .component import ComponentData, ComponentMode
from .enums import ComponentType
from .internals import Port

class VesselMode(ComponentMode):
    capacity: Annotated[ChemUnitQuantity, ChemQuantityValidator("ml")] = Field(
        default=ChemUnitQuantity("1 ml"),
        title="Component Capacity",
        description="Volumetric capacity of the component",
        json_schema_extra={
            "group": GroupParameterCategory.STATUS.value,
        },
    )
    top_access: int = Field(
        default=3,
        ge=1,
        title="Access at the top",
        description="Access connections at the top of the flask.",
        json_schema_extra={
            "group": GroupParameterCategory.PROPERTY.value,
            "editable": False,
            "lock_reason": "Internal Chosen",
        },
    )
    bottom_access: int = Field(
        default=2,
        ge=1,
        title="Access at the bottom",
        description="Access connections at the bottom of the flask.",
        json_schema_extra={
            "group": GroupParameterCategory.PROPERTY.value,
            "editable": False,
            "lock_reason": "Internal Chosen",
        },
    )


@dataclass
class VesselComponentData(ComponentData):
    COMPONENT_TYPE = ComponentType.UTENSIL
    capacity: ChemUnitQuantity
    top_access: int
    bottom_access: int

    @property
    def capacity_value(self) -> float:
        return self.capacity.to_base_units().magnitude
    
    def internal_structure(self):
        n = self.top_access + self.bottom_access
        self.port_pairs = [(i + 1,) for i in range(n + 1)]
        self.port_pairs = {i + 1: Port(number=i + 1, component=self.name) for i in range(n)}
        self.port_pairs[n + 1] = Port(number=n + 1, component=self.name, category=ConnectionType.HEAT)
