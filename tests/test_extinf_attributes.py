import pytest

import m3u8
from m3u8 import ParseError

IPTV = (
    "#EXTM3U\n"
    '#EXTINF:-1 tvg-id="one.tv" tvg-name="One" group-title="News, Weather",One TV\n'
    "http://example.com/one.ts\n"
)


def test_attributes_after_the_duration_are_parsed():
    segment = m3u8.loads(IPTV).segments[0]

    assert segment.duration == -1
    assert segment.title == "One TV"
    assert segment.extinf_attributes == {
        "tvg-id": "one.tv",
        "tvg-name": "One",
        "group-title": "News, Weather",
    }


def test_attributes_are_written_back():
    assert m3u8.loads(IPTV).dumps() == IPTV


def test_unquoted_attribute_values_are_read_and_written_quoted():
    segment = m3u8.loads("#EXTM3U\n#EXTINF:-1 tvg-id=one,T\nhttp://e.com/a.ts\n")

    assert segment.segments[0].extinf_attributes == {"tvg-id": "one"}
    assert '#EXTINF:-1 tvg-id="one",T' in segment.dumps()


def test_attributes_can_be_set_on_a_segment():
    segment = m3u8.Segment(uri="a.ts", duration=5, title="T")
    segment.extinf_attributes["tvg-id"] = "a"

    assert segment.dumps(None).splitlines()[0] == '#EXTINF:5 tvg-id="a",T'


@pytest.mark.parametrize(
    "line,duration,title",
    [
        ("#EXTINF:5,", 5, ""),
        ("#EXTINF:5,Title", 5, "Title"),
        ("#EXTINF: 10.5, spaced", 10.5, " spaced"),
        ("#EXTINF:5,Title, with comma", 5, "Title, with comma"),
        ("#EXTINF:5", 5, ""),
        ("#EXTINF:5 ,Title", 5, "Title"),
    ],
)
def test_lines_without_attributes_are_read_as_before(line, duration, title):
    segment = m3u8.loads(f"#EXTM3U\n{line}\na.ts\n").segments[0]

    assert segment.duration == duration
    assert segment.title == title
    assert segment.extinf_attributes == {}


def test_a_value_with_spaces_that_is_not_quoted_is_an_error():
    with pytest.raises(ParseError):
        m3u8.loads("#EXTM3U\n#EXTINF:-1 tvg-name=Some Name,T\na.ts\n")


def test_attributes_are_accepted_in_strict_mode():
    playlist = IPTV.replace("#EXTINF", "#EXT-X-TARGETDURATION:5\n#EXTINF")
    obj = m3u8.M3U8(playlist, strict=True)

    assert obj.segments[0].extinf_attributes["tvg-id"] == "one.tv"


def test_floating_point_duration_with_attributes_needs_version_3():
    playlist = '#EXTM3U\n#EXT-X-TARGETDURATION:6\n#EXTINF:5.5 tvg-id="a",T\na.ts\n'

    with pytest.raises(Exception, match="protocol version to 3"):
        m3u8.M3U8(playlist, strict=True)
    assert m3u8.M3U8(
        playlist.replace("#EXT-X-TARGET", "#EXT-X-VERSION:3\n#EXT-X-TARGET"),
        strict=True,
    )
