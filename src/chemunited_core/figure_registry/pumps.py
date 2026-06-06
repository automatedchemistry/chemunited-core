from dataclasses import dataclass
from typing import Annotated

from pydantic import Field, model_validator
from typing_extensions import Self, override

from chemunited_core.common.enums import GroupParameterCategory
from chemunited_core.components import (
    FlowSourceData,
    FlowSourceMode,
    PumpData,
    PutResult,
    ScheduledCommand,
)
from chemunited_core.utils.internal_quantity import ChemQuantityValidator, ChemUnitQuantity


class SyringePumpMode(FlowSourceMode):
    """User-configurable parameters for a syringe pump.

    Extends FlowSourceMode with syringe capacity, current fill level,
    and orientation.
    """

    syringe_volume: Annotated[ChemUnitQuantity, ChemQuantityValidator("ml")] = Field(
        default=ChemUnitQuantity("10 ml"),
        title="Syringe Capacity",
        description="Maximum physical capacity of the syringe barrel.",
        json_schema_extra={
            "group": GroupParameterCategory.PROPERTY.value,
        },
    )
    syringe_actual_volume: Annotated[ChemUnitQuantity, ChemQuantityValidator("ml")] = Field(
        default=ChemUnitQuantity("0 ml"),
        title="Current Fill Level",
        description="Amount of liquid currently loaded in the syringe (0 = empty).",
        json_schema_extra={
            "group": GroupParameterCategory.STATUS.value,
        },
    )
    direction_upward: bool = Field(
        default=True,
        title="Direction Upward",
        description=(
            "Orientation of the syringe. True = gas on top, port emits liquid. "
            "False = gas on bottom, port emits gas."
        ),
        json_schema_extra={
            "group": GroupParameterCategory.PROPERTY.value,
        },
    )

    @model_validator(mode="after")
    def _check_volume_bounds(self) -> Self:
        actual = self.syringe_actual_volume.to_base_units().magnitude
        cap = self.syringe_volume.to_base_units().magnitude
        if actual < 0:
            raise ValueError("syringe_actual_volume cannot be negative")
        if actual > cap:
            raise ValueError(
                f"syringe_actual_volume ({actual:.3e} m³) exceeds "
                f"syringe_volume ({cap:.3e} m³)"
            )
        return self


@dataclass
class SyringePumpData(FlowSourceData):
    syringe_volume: ChemUnitQuantity = ChemUnitQuantity("10 ml")
    syringe_actual_volume: ChemUnitQuantity = ChemUnitQuantity("0 ml")
    direction_upward: bool = True

    def put(self, command: str, **kwargs) -> PutResult:
        if command in ["infuse", "withdraw"]:
            flow_rate_si = ChemUnitQuantity(kwargs["rate"]).to_base_units().magnitude
            scheduled = []
            if "volume" in kwargs:
                volume_si = ChemUnitQuantity(kwargs["volume"]).to_base_units().magnitude
                dt = volume_si / flow_rate_si
                scheduled.append(ScheduledCommand(dt=dt, command="stop"))
            return PutResult(scheduled=scheduled)

        if command == "stop":
            return PutResult()

        raise ValueError(f"Unknown command '{command}' for SyringePumpData.")

    def apply(self, command: str, **kwargs) -> PutResult:
        if command in ["infuse", "withdraw"]:
            rate_str = kwargs["rate"]
            self.flow_rate = (
                ChemUnitQuantity(f"-{rate_str}")
                if command == "withdraw"
                else ChemUnitQuantity(rate_str)
            )
            self.sync_internal_state()

            scheduled: list[ScheduledCommand] = []
            if "volume" in kwargs:
                flow_rate_si = ChemUnitQuantity(rate_str).to_base_units().magnitude
                volume_si = ChemUnitQuantity(kwargs["volume"]).to_base_units().magnitude
                dt = volume_si / flow_rate_si
                scheduled.append(ScheduledCommand(dt=dt, command="stop"))
            return PutResult(scheduled=scheduled)

        if command == "stop":
            self.flow_rate = ChemUnitQuantity("0 ml/min")
            self.sync_internal_state()
            return PutResult()

        return PutResult()


@dataclass
class HPLCPumpData(PumpData):

    @override
    def apply(self, command: str, **kwargs) -> PutResult:
        if command == "start":
            self.flow_rate = ChemUnitQuantity(kwargs["rate"])
            self._sync()
        elif command == "stop":
            self.flow_rate = ChemUnitQuantity("0 ml/min")
            self._sync()
        return PutResult()
