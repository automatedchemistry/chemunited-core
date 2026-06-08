from importlib.abc import Traversable
from importlib.resources import files as _pkg_files

from chemunited_core.components import (
    BackPressureRegulatorData,
    BackPressureRegulatorMode,
    ComponentData,
    ComponentMode,
    JunctionData,
    JunctionMode,
    MassFlowControllerMode,
    NeutralComponentData,
    PlugFlowComponentData,
    PlugFlowMode,
    PressureControlData,
    PressureControlMode,
    PumpMode,
    VesselComponentData,
    VesselMode,
)
from chemunited_core.components import (
    FlowSourceMode as FlowSourceMode,
)
from chemunited_core.figure_registry.assemble import (
    Gantry3DData,
    Gantry3DMode,
)
from chemunited_core.figure_registry.controllers import MFCComponentData
from chemunited_core.figure_registry.pipes import (
    SeparatorData,
    SeparatorMode,
    SinkData,
    SinkMode,
    SourceData,
    SourceMode,
)
from chemunited_core.figure_registry.pumps import (
    HPLCPumpData,
    SyringePumpData,
    SyringePumpMode,
)
from chemunited_core.figure_registry.rotary_valve import (
    FourPortDistributionValveData,
    FourPortDistributionValveMode,
    FourPortFivePositionValveData,
    FourPortFivePositionValveMode,
    SixPortDistributionValveData,
    SixPortDistributionValveMode,
    SixPortTwoPositionValveData,
    SixPortTwoPositionValveMode,
    SixteenPortDistributionValveData,
    SixteenPortDistributionValveMode,
    ThreePortFourPositionValveData,
    ThreePortFourPositionValveMode,
    ThreePortTwoPositionValveData,
    ThreePortTwoPositionValveMode,
    TwelvePortDistributionValveData,
    TwelvePortDistributionValveMode,
    TwoPortDistributionValveData,
    TwoPortDistributionValveMode,
)
from chemunited_core.figure_registry.solenoid_valve import (
    Solenoid2WayValveMode,
    SolenoidValve2WayData,
    SolenoidValveData,
    SolenoidValveMode,
)
from chemunited_core.figure_registry.technical import (
    MultiChannelData,
    MultiChannelMode,
)
from chemunited_core.figure_registry.thermal import (
    PeltierCoolerTemperatureControlData,
    PeltierCoolerTemperatureControlMode,
    TemperatureControlData,
    TemperatureControlMode,
)
from chemunited_core.figure_registry.vessels import (
    FlowReactorData,
    FlowReactorMode,
    GlassBottleData,
    GlassBottleMode,
    PhotoReactorData,
    PhotoReactorMode,
    VialData,
    VialMode,
)

__all__ = [
    # functions / constants defined here
    "COMPONENTS",
    "get_figure_svg",
    "get_figure_path",
    "list_figures",
    # re-exported from chemunited_core.components
    "BackPressureRegulatorData",
    "BackPressureRegulatorMode",
    "ComponentData",
    "ComponentMode",
    "FlowSourceMode",
    "JunctionData",
    "JunctionMode",
    "MassFlowControllerMode",
    "NeutralComponentData",
    "PlugFlowComponentData",
    "PlugFlowMode",
    "PressureControlData",
    "PressureControlMode",
    "PumpMode",
    "VesselComponentData",
    "VesselMode",
    # re-exported from figure_registry submodules
    "Gantry3DData",
    "Gantry3DMode",
    "MFCComponentData",
    "SeparatorData",
    "SeparatorMode",
    "SinkData",
    "SinkMode",
    "SourceData",
    "SourceMode",
    "HPLCPumpData",
    "SyringePumpData",
    "SyringePumpMode",
    "FourPortDistributionValveData",
    "FourPortDistributionValveMode",
    "FourPortFivePositionValveData",
    "FourPortFivePositionValveMode",
    "SixPortDistributionValveData",
    "SixPortDistributionValveMode",
    "SixPortTwoPositionValveData",
    "SixPortTwoPositionValveMode",
    "SixteenPortDistributionValveData",
    "SixteenPortDistributionValveMode",
    "ThreePortFourPositionValveData",
    "ThreePortFourPositionValveMode",
    "ThreePortTwoPositionValveData",
    "ThreePortTwoPositionValveMode",
    "TwelvePortDistributionValveData",
    "TwelvePortDistributionValveMode",
    "TwoPortDistributionValveData",
    "TwoPortDistributionValveMode",
    "Solenoid2WayValveMode",
    "SolenoidValve2WayData",
    "SolenoidValveData",
    "SolenoidValveMode",
    "MultiChannelData",
    "MultiChannelMode",
    "PeltierCoolerTemperatureControlData",
    "PeltierCoolerTemperatureControlMode",
    "TemperatureControlData",
    "TemperatureControlMode",
    "FlowReactorData",
    "FlowReactorMode",
    "GlassBottleData",
    "GlassBottleMode",
    "PhotoReactorData",
    "PhotoReactorMode",
    "VialData",
    "VialMode",
]

_FIGURES = _pkg_files("chemunited_core.figure_registry.figures")


def get_figure_svg(name: str) -> str:
    """Return SVG markup for *name* (filename without .svg extension)."""
    return _FIGURES.joinpath(f"{name}.svg").read_text(encoding="utf-8")


def get_figure_path(name: str) -> Traversable:
    """Return a Traversable for the SVG file (zip-safe; use open() or as_file())."""
    return _FIGURES.joinpath(f"{name}.svg")


def list_figures() -> list[str]:
    """Return sorted list of available figure names (without .svg extension)."""
    return sorted(p.name[:-4] for p in _FIGURES.iterdir() if p.name.endswith(".svg"))


COMPONENTS: dict[str, tuple[type[ComponentData], type[ComponentMode]]] = {
    # analytics
    "HPLCControl": (ComponentData, ComponentMode),
    "IRControl": (ComponentData, ComponentMode),
    "MSControl": (ComponentData, ComponentMode),
    "NMRControl": (ComponentData, ComponentMode),
    # assembly
    "Gantry3D": (Gantry3DData, Gantry3DMode),
    "LengthControl": (NeutralComponentData, ComponentMode),
    # pipes
    "BackPressureRegulator": (
        BackPressureRegulatorData,
        BackPressureRegulatorMode,
    ),
    "Distributor": (JunctionData, JunctionMode),
    "MFCComponent": (MFCComponentData, MassFlowControllerMode),
    "Sink": (SinkData, SinkMode),
    "Source": (SourceData, SourceMode),
    "Separator": (SeparatorData, SeparatorMode),
    # pumps
    "HPLCPump": (HPLCPumpData, PumpMode),
    "SyringePump": (SyringePumpData, SyringePumpMode),
    # sensors
    "FlowMeter": (ComponentData, ComponentMode),
    "PhidgetBubbleSensorComponent": (ComponentData, ComponentMode),
    "PhidgetBubbleSensorPowerComponent": (NeutralComponentData, ComponentMode),
    "PhotoSensor": (NeutralComponentData, ComponentMode),
    "PressureControl": (PressureControlData, PressureControlMode),
    "PressureSensor": (ComponentData, ComponentMode),
    # technical
    "MultiChannelADC": (MultiChannelData, MultiChannelMode),
    "MultiChannelDAC": (MultiChannelData, MultiChannelMode),
    "MultiChannelRelay": (MultiChannelData, MultiChannelMode),
    "PowerControl": (NeutralComponentData, ComponentMode),
    "PowerSwitch": (NeutralComponentData, ComponentMode),
    # thermal
    "PeltierCoolerTemperatureControl": (
        PeltierCoolerTemperatureControlData,
        PeltierCoolerTemperatureControlMode,
    ),
    "TemperatureControl": (TemperatureControlData, TemperatureControlMode),
    # valve - rotary
    "FourPortDistributionValve": (
        FourPortDistributionValveData,
        FourPortDistributionValveMode,
    ),
    "FourPortFivePositionValve": (
        FourPortFivePositionValveData,
        FourPortFivePositionValveMode,
    ),
    "SixPortDistributionValve": (
        SixPortDistributionValveData,
        SixPortDistributionValveMode,
    ),
    "SixPortTwoPositionValve": (
        SixPortTwoPositionValveData,
        SixPortTwoPositionValveMode,
    ),
    "SixteenPortDistributionValve": (
        SixteenPortDistributionValveData,
        SixteenPortDistributionValveMode,
    ),
    "ThreePortFourPositionValve": (
        ThreePortFourPositionValveData,
        ThreePortFourPositionValveMode,
    ),
    "ThreePortTwoPositionValve": (
        ThreePortTwoPositionValveData,
        ThreePortTwoPositionValveMode,
    ),
    "TwelvePortDistributionValve": (
        TwelvePortDistributionValveData,
        TwelvePortDistributionValveMode,
    ),
    "TwoPortDistributionValve": (
        TwoPortDistributionValveData,
        TwoPortDistributionValveMode,
    ),
    # valve - solenoid
    "SolenoidValve": (SolenoidValveData, SolenoidValveMode),
    "SolenoidValve2Way": (SolenoidValve2WayData, Solenoid2WayValveMode),
    # vessels
    "CustomFlask": (VesselComponentData, VesselMode),
    "FlowReactor": (FlowReactorData, FlowReactorMode),
    "GlassBottle": (GlassBottleData, GlassBottleMode),
    "Loop": (PlugFlowComponentData, PlugFlowMode),
    "PhotoReactor": (PhotoReactorData, PhotoReactorMode),
    "Vial": (VialData, VialMode),
}
