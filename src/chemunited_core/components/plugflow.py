from dataclasses import dataclass
from typing import Annotated

import numpy as np
from pydantic import Field

from ..common.enums import GroupParameterCategory
from ..utils.internal_quantity import ChemQuantityValidator, ChemUnitQuantity
from .component import ComponentData, ComponentMode
from .internals import InternalEdge, Port


class PlugFlowMode(ComponentMode):
    """Concrete mode alias for differential volumetric components."""

    length: Annotated[ChemUnitQuantity, ChemQuantityValidator("mm")] = Field(
        default=ChemUnitQuantity("100 mm"),
        title="Length",
        description="Length of the connection",
        json_schema_extra={
            "group": GroupParameterCategory.PROPERTY.value,
        },
    )
    diameter: Annotated[ChemUnitQuantity, ChemQuantityValidator("mm")] = Field(
        default=ChemUnitQuantity("1 mm"),
        title="Diameter",
        description="Diameter of the connection",
        json_schema_extra={
            "group": GroupParameterCategory.PROPERTY.value,
        },
    )


@dataclass
class PlugFlowComponentData(ComponentData):
    """Runtime dataclass for plug-flow (tubular) reactor components."""

    length: ChemUnitQuantity
    diameter: ChemUnitQuantity

    @property
    def capacity(self) -> float:
        return self.length_value * np.pi * self.diameter**2 / 4  # m**3

    @property
    def length_value(self) -> float:
        return self.length.to_base_units().magnitude

    @property
    def diameter_value(self) -> float:
        return self.diameter.to_base_units().magnitude

    def internal_structure(self, update: bool = False):
        if update:
            self.internal_edges[(1, 2)].length = self.length_value
            self.internal_edges[(1, 2)].diameter = self.diameter_value
            return
        self.port_pairs = [(1, 2)]
        self.ports_by_number = {
            1: Port(number=1, component=self.name, relative_position=(-1, 0)),
            2: Port(number=2, component=self.name, relative_position=(1, 0)),
        }
        self.internal_edges = {
            (1, 2): InternalEdge(
                origin_port=1,
                destination_port=2,
                length=self.length_value,
                diameter=self.diameter_value,
            )
        }
