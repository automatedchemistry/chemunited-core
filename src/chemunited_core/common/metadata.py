from dataclasses import MISSING, dataclass, fields, is_dataclass
from pydantic import BaseModel
from typing import Self


@dataclass
class Element:

    @classmethod
    def from_mode(cls: type[Self], mode: BaseModel) -> Self:
        if not isinstance(mode, BaseModel):
            raise TypeError(
                f"{cls.__name__}.from_mode expects a Pydantic BaseModel instance, "
                f"got {type(mode).__name__}."
            )

        if not is_dataclass(cls):
            raise TypeError(f"{cls.__name__} must be a dataclass to use from_mode.")

        init_values = {}
        missing_fields: list[str] = []

        for field in fields(cls):
            if not field.init:
                continue

            if hasattr(mode, field.name):
                init_values[field.name] = getattr(mode, field.name)
                continue

            has_default = field.default is not MISSING
            has_default_factory = field.default_factory is not MISSING

            if has_default or has_default_factory:
                continue

            missing_fields.append(field.name)

        if missing_fields:
            missing_names = ", ".join(f"'{name}'" for name in missing_fields)
            raise TypeError(
                f"Cannot build {cls.__name__} from {type(mode).__name__}: "
                f"missing required field(s) {missing_names}."
            )

        return cls(**init_values)
