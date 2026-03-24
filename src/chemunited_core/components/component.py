from dataclasses import dataclass, field
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator

from ..common.enums import GroupParameterCategory
from ..common.metadata import Element
from .enums import ComponentType
from .internals import Port, InternalEdge

EdgeKey = tuple[int, int]


class ComponentMode(BaseModel, populate_by_name=True):
    name: str = Field(
        default="",
        title="Component Name",
        description="Component name in the Orchestration",
        json_schema_extra={
            "group": GroupParameterCategory.GENERAL.value,
            "editable": False,
        },
    )
    figure: str = Field(
        default="",
        title="Component Figure",
        description="Component Figure Class Representation",
        json_schema_extra={
            "group": GroupParameterCategory.GENERAL.value,
            "editable": False,
            "callable": False,
            "lock_reason": "Internal Classification",
        },
    )
    position: tuple[float, float] = Field(
        default=(0, 0),
        title="Component Position",
        description="Component Position in the Scene",
        json_schema_extra={"visible": False},
    )
    angle: int = Field(
        default=0,
        ge=0,
        le=360,
        title="Component Angle",
        description="Component Position in the Scene",
        json_schema_extra={"group": GroupParameterCategory.GENERAL.value},
    )

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        if "." in value or "_" in value:
            raise ValueError("Field 'name' must not contain '.' or '_' characters.")
        return value


@dataclass
class ComponentData(Element):
    name: str
    figure: str
    position: tuple[float, float]
    angle: int
    COMPONENT_TYPE: ClassVar[ComponentType] = ComponentType.ELECTRONIC
    port_pairs: list[tuple[int, int]] = field(default_factory=list, init=False)
    ports_by_number: dict[int, Port] = field(default_factory=dict, init=False)
    internal_edges: dict[EdgeKey, InternalEdge] = field(default_factory=dict, init=False)

    """ Properties """

    @property
    def component_type(self) -> ComponentType:
        return type(self).COMPONENT_TYPE

    @property
    def is_electronic(self) -> bool:
        return self.component_type == ComponentType.ELECTRONIC

    """ Initialization """

    def __post_init__(self):
        self.internal_structure()
    
    def internal_structure(self):
        self.port_pairs = [(1, 2)]
        self.ports_by_number = {
            1: Port(number=1, component=self.name),
            2: Port(number=2, component=self.name)
        }


@dataclass
class NeutralComponentData(ComponentData):
    def __post_init__(self):
        ...


