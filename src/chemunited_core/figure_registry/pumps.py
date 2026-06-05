from dataclasses import dataclass

from typing_extensions import override

from chemunited_core.components import (
    FlowSourceData,
    PumpData,
    PutResult,
    ScheduledCommand,
)
from chemunited_core.utils.internal_quantity import ChemUnitQuantity


class SyringePumpData(FlowSourceData):

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
