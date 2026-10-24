import pytest

import m3u8
from m3u8 import ParseError

HEADER = "#EXTM3U\n#EXT-X-TARGETDURATION:5\n"
SEGMENT = "#EXTINF:5,\na.ts\n"


def test_tag_that_only_starts_like_another_tag_is_not_that_tag():
    obj = m3u8.loads(
        HEADER
        + "#EXT-X-KEYFRAME:FOO=1\n"
        + "#EXT-X-MEDIA-FOO:A=1\n"
        + "#EXT-X-ENDLISTED\n"
        + SEGMENT
    )

    assert obj.keys == [None]
    assert len(obj.media) == 0
    assert not obj.is_endlist


def test_byte_order_mark_is_ignored():
    obj = m3u8.loads("﻿" + HEADER + SEGMENT)

    assert obj.target_duration == 5
    assert len(obj.segments) == 1


def test_unicode_line_separators_do_not_split_a_line():
    obj = m3u8.loads(HEADER + "#EXTINF:5,a b\u0085c\nx.ts\n")

    assert [segment.title for segment in obj.segments] == ["a b\u0085c"]
    assert obj.segments[0].uri == "x.ts"


def test_carriage_returns_still_end_a_line():
    obj = m3u8.loads("#EXTM3U\r#EXT-X-TARGETDURATION:5\r\n#EXTINF:5,\r\na.ts")

    assert obj.segments[0].uri == "a.ts"


def test_title_can_contain_the_name_of_the_tag():
    obj = m3u8.loads(HEADER + "#EXTINF:5,see #EXTINF: here\nx.ts\n")

    assert obj.segments[0].title == "see #EXTINF: here"


@pytest.mark.parametrize(
    "line",
    [
        "#EXT-X-KEY",
        "#EXT-X-KEY:METHOD",
        "#EXT-X-SESSION-KEY:METHOD",
        "#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=1",
        "#EXT-X-VERSION",
        "#EXT-X-TARGETDURATION",
        "#EXT-X-PROGRAM-DATE-TIME:nope",
        "#EXTINF:abc,",
    ],
)
def test_malformed_tag_raises_parse_error_with_its_line(line):
    with pytest.raises(ParseError) as error:
        m3u8.loads(f"#EXTM3U\n{line}\n#EXTINF:5,\na.ts\n")

    assert error.value.lineno == 2
    assert error.value.line == line


def test_parse_error_is_a_value_error():
    assert issubclass(ParseError, ValueError)
    with pytest.raises(ValueError):
        m3u8.loads("#EXTM3U\n#EXT-X-VERSION\n")


def test_exceptions_of_a_custom_tags_parser_are_not_changed():
    def custom_tags_parser(line, lineno, data, state):
        if line.startswith("#EXT-X-BOOM"):
            raise ValueError("custom")

    with pytest.raises(ValueError, match="custom") as error:
        m3u8.loads(
            HEADER + "#EXT-X-BOOM\n" + SEGMENT, custom_tags_parser=custom_tags_parser
        )

    assert not isinstance(error.value, ParseError)
