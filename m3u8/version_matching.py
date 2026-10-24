from m3u8 import protocol
from m3u8.version_matching_rules import VersionMatchingError, available_rules

# The protocol version of a playlist without an EXT-X-VERSION tag
DEFAULT_VERSION = 1


def get_version(file_lines: list[str]):
    for line in file_lines:
        line = line.strip()
        if line.startswith(protocol.ext_x_version + ":"):
            try:
                return float(line.split(":", 1)[1])
            except ValueError:
                return None

    return DEFAULT_VERSION


def valid_in_all_rules(
    line_number: int,
    line: str,
    version: float,
    file_lines: list[str] | None = None,
) -> list[VersionMatchingError]:
    errors = []
    for rule in available_rules:
        validator = rule(version, line_number, line, file_lines)

        if not validator.validate():
            errors.append(validator.get_error())

    return errors


def validate(file_lines: list[str]) -> list[VersionMatchingError]:
    found_version = get_version(file_lines)
    if found_version is None:
        return []

    errors = []
    for number, line in enumerate(file_lines, 1):
        errors_in_line = valid_in_all_rules(number, line, found_version, file_lines)
        errors.extend(errors_in_line)

    return errors
