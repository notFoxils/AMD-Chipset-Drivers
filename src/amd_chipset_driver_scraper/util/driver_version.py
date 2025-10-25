from dataclasses import dataclass
from functools import total_ordering
from typing import Final, Self, final, override

import typer


@final
@dataclass
@total_ordering
class DriverVersion:
    version_elements: Final[tuple[int, ...]]

    @override
    def __init__(self, version_elements: tuple[int, ...]) -> None:
        self.version_elements = version_elements

    def __gt__(self, other: Self) -> bool:
        self_num_elements: Final[int] = len(self.version_elements)
        less_specific_driver_version_num_elements: Final[int] = min(self_num_elements, len(other.version_elements))

        for version_element_index in range(less_specific_driver_version_num_elements):
            if self.version_elements[version_element_index] == other.version_elements[version_element_index]:
                continue

                # If (element of self) is greater than (element of other), return true
            return self.version_elements[version_element_index] > other.version_elements[version_element_index]

        # If self is more specific, return true
        return self_num_elements > less_specific_driver_version_num_elements

    @override
    def __str__(self) -> str:
        return str.join(
            ".",
            map(str, self.version_elements)
        )

    @staticmethod
    def from_string(string: str) -> ('DriverVersion | None'):
        version_element_strs: Final[list[str]] = string.split('.')
        version_element_strs_length: Final[int] = len(version_element_strs)

        version_element_ints: Final[list[int]] = [0] * version_element_strs_length
        for version_element_str_index in range(version_element_strs_length):
            try:
                version_element_ints[version_element_str_index] = int(version_element_strs[version_element_str_index])
            except ValueError:
                return None

        return DriverVersion(tuple(
            version_element_ints
        ))

    @staticmethod
    def typer_parse(string: str) -> 'DriverVersion':
        driver_version = DriverVersion.from_string(str(string))
        if driver_version is None:
            raise typer.BadParameter(f"'{string}'")

        return driver_version
