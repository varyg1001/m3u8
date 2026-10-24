import pytest

from m3u8 import version_matching
from m3u8.version_matching_rules import (
    ValidEXTXBYTERANGEOrEXTXIFRAMESONLY,
    ValidFloatingPointEXTINF,
    ValidIVInEXTXKEY,
)


def test_invalid_iv_in_EXT_X_KEY():
    validator = ValidIVInEXTXKEY(
        version=1,
        line_number=1,
        line="#EXT-X-KEY: METHOD=AES-128, IV=0x123456789ABCDEF0123456789ABCDEF0, URI=https://example.com/key.bin",
    )

    assert not validator.validate()


def test_valid_iv_in_EXT_X_KEY():
    examples = [
        {
            "line": "#EXT-X-KEY: METHOD=AES-128, URI=https://example.com/key.bin",
            "version": 1,
            "expected": True,
        },
        {
            "line": "#EXT-X-KEY: METHOD=AES-128, IV=0x123456789ABCDEF0123456789ABCDEF0, URI=https://example.com/key.bin",
            "version": 2,
            "expected": True,
        },
        {
            "line": "#EXT-X-KEY: METHOD=AES-128, IV=0x123456789ABCDEF0123456789ABCDEF0, URI=https://example.com/key.bin",
            "version": 3,
            "expected": True,
        },
        # Invalid case
        {
            "line": "#EXT-X-KEY: METHOD=AES-128, IV=0x123456789ABCDEF0123456789ABCDEF0, URI=https://example.com/key.bin",
            "version": 1,
            "expected": False,
        },
    ]

    for example in examples:
        validator = ValidIVInEXTXKEY(
            version=example["version"],
            line_number=1,
            line=example["line"],
        )
        assert validator.validate() == example["expected"]


def test_invalid_floating_point_EXTINF():
    examples = [
        {
            "line": "#EXTINF: 10.5,",
            "version": 2,
        },
        {
            "line": "#EXTINF: A,",
            "version": 3,
        },
    ]

    for example in examples:
        validator = ValidFloatingPointEXTINF(
            version=example["version"],
            line_number=1,
            line=example["line"],
        )
        assert not validator.validate()


def test_valid_floating_point_EXTINF():
    examples = [
        {
            "line": "#EXTINF: 10,",
            "version": 2,
        },
        {
            "line": "#EXTINF: 10.5,",
            "version": 3,
        },
        {
            "line": "#EXTINF: 10.5,",
            "version": 4,
        },
    ]

    for example in examples:
        validator = ValidFloatingPointEXTINF(
            version=example["version"],
            line_number=1,
            line=example["line"],
        )
        assert validator.validate()


def test_invalid_EXT_X_BYTERANGE_or_EXT_X_I_FRAMES_ONLY():
    examples = [
        {
            "line": "#EXT-X-BYTERANGE: 200000@1000",
            "version": 3,
        },
        {
            "line": "#EXT-X-I-FRAMES-ONLY",
            "version": 3,
        },
    ]

    for example in examples:
        validator = ValidEXTXBYTERANGEOrEXTXIFRAMESONLY(
            version=example["version"],
            line_number=1,
            line=example["line"],
        )
        assert not validator.validate()


def test_valid_EXT_X_BYTERANGE_or_EXT_X_I_FRAMES_ONLY():
    examples = [
        {
            "line": "#EXT-X-BYTERANGE: 200000@1000",
            "version": 4,
        },
        {
            "line": "#EXT-X-I-FRAMES-ONLY",
            "version": 4,
        },
        {
            "line": "#EXT-X-BYTERANGE: 200000@1000",
            "version": 5,
        },
        {
            "line": "#EXT-X-I-FRAMES-ONLY",
            "version": 5,
        },
    ]

    for example in examples:
        validator = ValidEXTXBYTERANGEOrEXTXIFRAMESONLY(
            version=example["version"],
            line_number=1,
            line=example["line"],
        )
        assert validator.validate()


def _errors(lines, version=None):
    if version is not None:
        lines = [f"#EXT-X-VERSION:{version}", *lines]
    return version_matching.validate(lines)


# (line, the lowest protocol version that allows it), see section 8 of
# draft-pantos-hls-rfc8216bis
REQUIRED_VERSIONS = [
    ('#EXT-X-KEY:METHOD=AES-128,URI="k",IV=0x1', 2),
    ("#EXTINF:9.009,", 3),
    ("#EXT-X-BYTERANGE:100@0", 4),
    ("#EXT-X-I-FRAMES-ONLY", 4),
    ('#EXT-X-KEY:METHOD=SAMPLE-AES,URI="k"', 5),
    ('#EXT-X-KEY:METHOD=AES-128,URI="k",KEYFORMAT="identity"', 5),
    ('#EXT-X-KEY:METHOD=AES-128,URI="k",KEYFORMATVERSIONS="1"', 5),
    ('#EXT-X-MAP:URI="init.mp4"', 6),
    ('#EXT-X-MEDIA:TYPE=CLOSED-CAPTIONS,GROUP-ID="cc",INSTREAM-ID="SERVICE1"', 7),
    ('#EXT-X-DEFINE:NAME="a",VALUE="1"', 8),
    ("segment-{$a}.ts", 8),
    ("#EXT-X-SKIP:SKIPPED-SEGMENTS=3", 9),
    ('#EXT-X-SKIP:SKIPPED-SEGMENTS=3,RECENTLY-REMOVED-DATERANGES="a"', 10),
    ('#EXT-X-DEFINE:QUERYPARAM="token"', 11),
    ('#EXT-X-STREAM-INF:BANDWIDTH=1,REQ-VIDEO-LAYOUT="CH-STEREO"', 12),
    ('#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="a",INSTREAM-ID="x"', 13),
]


@pytest.mark.parametrize("line,required", REQUIRED_VERSIONS)
def test_line_needs_its_minimum_protocol_version(line, required):
    assert _errors([line], required) == []
    assert len(_errors([line], required - 1)) >= 1


def test_closed_captions_instream_id_needs_version_7_only_for_service():
    service = '#EXT-X-MEDIA:TYPE=CLOSED-CAPTIONS,GROUP-ID="cc",INSTREAM-ID="SERVICE1"'
    cc = '#EXT-X-MEDIA:TYPE=CLOSED-CAPTIONS,GROUP-ID="cc",INSTREAM-ID="CC1"'

    assert len(_errors([service], 6)) == 1
    assert _errors([service], 7) == []
    assert _errors([cc], 1) == []


def test_map_needs_version_5_in_an_i_frames_only_playlist():
    lines = ["#EXT-X-I-FRAMES-ONLY", '#EXT-X-MAP:URI="init.mp4"']

    assert _errors(lines, 5) == []
    assert any("EXT-X-MAP" in error.line for error in _errors(lines, 4))


def test_other_tags_and_attribute_values_are_not_mistaken_for_features():
    lines = [
        '#EXT-X-KEY:METHOD=AES-128,URI="https://drive.example.com/key"',
        '#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="a",NAME="REQ-IV",URI="a.m3u8"',
        "#EXT-X-BYTERANGE-ISH:1",
        "#EXTINF:10,",
    ]

    assert _errors(lines, 1) == []


def test_playlist_without_version_is_version_1():
    assert len(_errors(["#EXTINF:9.009,"])) == 1
    assert _errors(["#EXTINF:9,"]) == []


def test_malformed_version_is_not_validated():
    assert _errors(["#EXT-X-VERSION:x", "#EXTINF:9.009,"]) == []


def test_line_numbers_start_at_one():
    errors = _errors(["#EXTINF:9.009,"], 1)

    assert errors[0].line_number == 2
