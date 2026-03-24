from enum import StrEnum


class GroupParameterCategory(StrEnum):
    GENERAL = "General"
    PROPERTY = "Property"
    STATUS = "Status"


class ConnectionType(StrEnum):
    FLOW = "flow"
    MOVEMENT = "movement"
    HEAT = "heat"
    ELECTRONIC = "electronic"

