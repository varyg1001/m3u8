import re
from dataclasses import dataclass
from typing import Optional

from m3u8 import protocol

ATTRIBUTE_PATTERN = re.compile(r'([A-Za-z0-9-]+)\s*=\s*("[^"]*"|[^,]*)')


@dataclass
class VersionMatchingError(Exception):
    line_number: int
    line: str
    how_to_fix: str = "Please fix the version matching error."
    description: str = "There is a version matching error in the file."

    def __str__(self):
        return (
            "Version matching error found in the file when parsing in strict mode.\n"
            f"Line {self.line_number}: {self.description}\n"
            f"Line content: {self.line}\n"
            f"How to fix: {self.how_to_fix}"
            "\n"
        )


def is_tag(line: str, tag: str) -> bool:
    """Whether the line is the given tag, not another tag that starts with its name."""
    return line == tag or line.startswith((tag + ":", tag + " "))


def get_attributes(line: str) -> dict[str, str]:
    """The attributes of a tag line, with upper cased names and without quotes."""
    if ":" not in line:
        return {}
    attributes = {}
    for name, value in ATTRIBUTE_PATTERN.findall(line.split(":", 1)[1]):
        attributes[name.upper()] = value.strip().strip('"')
    return attributes


class VersionMatchRuleBase:
    description: str = ""
    how_to_fix: str = ""
    version: float
    line_number: int
    line: str
    file_lines: list[str]

    def __init__(
        self,
        version: float,
        line_number: int,
        line: str,
        file_lines: Optional[list[str]] = None,
    ) -> None:
        self.version = version
        self.line_number = line_number
        self.line = line.strip()
        self.file_lines = file_lines or []

    def validate(self):
        raise NotImplementedError

    def get_error(self):
        return VersionMatchingError(
            line_number=self.line_number,
            line=self.line,
            description=self.description,
            how_to_fix=self.how_to_fix,
        )


class MinimumVersionRule(VersionMatchRuleBase):
    """A line that needs a minimum protocol version when it uses a feature."""

    required_version: float = 1

    def uses_feature(self) -> bool:
        raise NotImplementedError

    def validate(self):
        return not self.uses_feature() or self.version >= self.required_version

    @property
    def how_to_fix(self):  # type: ignore[override]
        return f"Change the protocol version to {self.required_version} or higher."


class ValidIVInEXTXKEY(MinimumVersionRule):
    description = (
        "You must use at least protocol version 2 if you have IV in EXT-X-KEY."
    )
    required_version = 2

    def uses_feature(self):
        return is_tag(self.line, protocol.ext_x_key) and "IV" in get_attributes(
            self.line
        )


class ValidFloatingPointEXTINF(MinimumVersionRule):
    description = "You must use at least protocol version 3 if you have floating point EXTINF duration values."
    required_version = 3

    def validate(self):
        if not is_tag(self.line, protocol.extinf):
            return True

        duration = self.line.replace(protocol.extinf + ":", "").split(",", 1)[0]
        try:
            float(duration)
        except ValueError:
            return False

        return "." not in duration or self.version >= self.required_version


class ValidEXTXBYTERANGEOrEXTXIFRAMESONLY(MinimumVersionRule):
    description = "You must use at least protocol version 4 if you have EXT-X-BYTERANGE or EXT-X-I-FRAMES-ONLY."
    required_version = 4

    def uses_feature(self):
        return is_tag(self.line, protocol.ext_x_byterange) or is_tag(
            self.line, protocol.ext_i_frames_only
        )


class ValidSampleAESKeyFormatInEXTXKEY(MinimumVersionRule):
    description = (
        "You must use at least protocol version 5 if you have METHOD=SAMPLE-AES, "
        "KEYFORMAT or KEYFORMATVERSIONS in EXT-X-KEY."
    )
    required_version = 5

    def uses_feature(self):
        if not is_tag(self.line, protocol.ext_x_key):
            return False
        attributes = get_attributes(self.line)
        return (
            attributes.get("METHOD") == "SAMPLE-AES"
            or "KEYFORMAT" in attributes
            or "KEYFORMATVERSIONS" in attributes
        )


class ValidEXTXMAP(MinimumVersionRule):
    description = (
        "You must use at least protocol version 5 if you have EXT-X-MAP, "
        "or 6 if the playlist does not contain EXT-X-I-FRAMES-ONLY."
    )

    @property
    def required_version(self):  # type: ignore[override]
        i_frames_only = any(
            is_tag(line.strip(), protocol.ext_i_frames_only) for line in self.file_lines
        )
        return 5 if i_frames_only else 6

    def uses_feature(self):
        return is_tag(self.line, protocol.ext_x_map)


class ValidServiceInstreamIdInEXTXMEDIA(MinimumVersionRule):
    description = (
        'You must use at least protocol version 7 if you have INSTREAM-ID="SERVICE" '
        "values in EXT-X-MEDIA."
    )
    required_version = 7

    def uses_feature(self):
        if not is_tag(self.line, protocol.ext_x_media):
            return False
        return get_attributes(self.line).get("INSTREAM-ID", "").startswith("SERVICE")


class ValidVariableSubstitution(MinimumVersionRule):
    description = (
        "You must use at least protocol version 8 if you have EXT-X-DEFINE "
        "or variable references."
    )
    required_version = 8

    def uses_feature(self):
        return is_tag(self.line, protocol.ext_x_define) or "{$" in self.line


class ValidEXTXSKIP(MinimumVersionRule):
    description = "You must use at least protocol version 9 if you have EXT-X-SKIP."
    required_version = 9

    def uses_feature(self):
        return is_tag(self.line, protocol.ext_x_skip)


class ValidDateRangesInEXTXSKIP(MinimumVersionRule):
    description = (
        "You must use at least protocol version 10 if EXT-X-SKIP replaces "
        "EXT-X-DATERANGE tags (RECENTLY-REMOVED-DATERANGES)."
    )
    required_version = 10

    def uses_feature(self):
        return is_tag(
            self.line, protocol.ext_x_skip
        ) and "RECENTLY-REMOVED-DATERANGES" in get_attributes(self.line)


class ValidQueryParamInEXTXDEFINE(MinimumVersionRule):
    description = (
        "You must use at least protocol version 11 if you have QUERYPARAM "
        "in EXT-X-DEFINE."
    )
    required_version = 11

    def uses_feature(self):
        return is_tag(self.line, protocol.ext_x_define) and "QUERYPARAM" in (
            get_attributes(self.line)
        )


class ValidReqAttributes(MinimumVersionRule):
    description = 'You must use at least protocol version 12 if you have an attribute whose name starts with "REQ-".'
    required_version = 12

    def uses_feature(self):
        return self.line.startswith("#EXT") and any(
            name.startswith("REQ-") for name in get_attributes(self.line)
        )


class ValidInstreamIdInEXTXMEDIA(MinimumVersionRule):
    description = (
        "You must use at least protocol version 13 if you have INSTREAM-ID in "
        "EXT-X-MEDIA with a TYPE other than CLOSED-CAPTIONS."
    )
    required_version = 13

    def uses_feature(self):
        if not is_tag(self.line, protocol.ext_x_media):
            return False
        attributes = get_attributes(self.line)
        return (
            "INSTREAM-ID" in attributes and attributes.get("TYPE") != "CLOSED-CAPTIONS"
        )


available_rules: list[type[VersionMatchRuleBase]] = [
    ValidIVInEXTXKEY,
    ValidFloatingPointEXTINF,
    ValidEXTXBYTERANGEOrEXTXIFRAMESONLY,
    ValidSampleAESKeyFormatInEXTXKEY,
    ValidEXTXMAP,
    ValidServiceInstreamIdInEXTXMEDIA,
    ValidVariableSubstitution,
    ValidEXTXSKIP,
    ValidDateRangesInEXTXSKIP,
    ValidQueryParamInEXTXDEFINE,
    ValidReqAttributes,
    ValidInstreamIdInEXTXMEDIA,
]
