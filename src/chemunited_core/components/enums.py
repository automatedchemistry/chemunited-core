from enum import Enum, auto


class ComponentType(Enum):
    ELECTRONIC = 0
    UTENSIL = 1


class PortAccess(Enum):
    BOTTOM = 0
    TOP = 1


class InternalEdgeRole(Enum):
    TRANSPORT = auto()  # has physical length/diameter — tube, reactor cell
    JUNCTION = auto()  # connects port to inventory node — vessel, junction


class PortClosure(Enum):
    CAPPED = auto()
    OPEN = auto()
