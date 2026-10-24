"""Attributes and tags must survive parsing and dumping again."""

import pytest

import m3u8

HEADER = "#EXTM3U\n#EXT-X-TARGETDURATION:5\n"
VARIANT = "#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=1\nvideo.m3u8\n"
SEGMENT = "#EXTINF:5,\na.ts\n"

ROUND_TRIPS = {
    "daterange duration zero": (
        HEADER
        + '#EXT-X-DATERANGE:ID="a",START-DATE="2026-01-01T00:00:00Z",DURATION=0\n'
        + SEGMENT,
        ["DURATION=0"],
    ),
    "daterange planned duration zero": (
        HEADER
        + '#EXT-X-DATERANGE:ID="a",START-DATE="2026-01-01T00:00:00Z",PLANNED-DURATION=0\n'
        + SEGMENT,
        ["PLANNED-DURATION=0"],
    ),
    "daterange unknown attribute": (
        HEADER
        + '#EXT-X-DATERANGE:ID="a",START-DATE="2026-01-01T00:00:00Z",CUE="PRE"\n'
        + SEGMENT,
        ['CUE="PRE"'],
    ),
    "server control zero values": (
        HEADER + "#EXT-X-SERVER-CONTROL:HOLD-BACK=0,CAN-SKIP-UNTIL=0\n" + SEGMENT,
        ["HOLD-BACK=0", "CAN-SKIP-UNTIL=0"],
    ),
    "bitrate zero": (HEADER + "#EXT-X-BITRATE:0\n" + SEGMENT, ["#EXT-X-BITRATE:0"]),
    "session data empty value": (
        VARIANT + '#EXT-X-SESSION-DATA:DATA-ID="x",VALUE=""\n',
        ['VALUE=""'],
    ),
    "tiles": (
        HEADER + "#EXT-X-TILES:RESOLUTION=320x180,LAYOUT=5x2,DURATION=2.5\n" + SEGMENT,
        ["#EXT-X-TILES:RESOLUTION=320x180,LAYOUT=5x2,DURATION=2.5"],
    ),
    "media extra attributes": (
        VARIANT
        + '#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="a",NAME="n",THUMBNAILS="t",FOO=bar\n',
        ['THUMBNAILS="t"', "FOO=bar"],
    ),
    "key extra attributes": (
        HEADER + '#EXT-X-KEY:METHOD=AES-128,URI="k",FOO="bar"\n' + SEGMENT,
        ['FOO="bar"'],
    ),
    "part unknown attribute": (
        HEADER + '#EXT-X-PART:DURATION=1,URI="p",FOO=1\n' + SEGMENT,
        ["FOO=1"],
    ),
    "start unknown attribute": (
        HEADER + "#EXT-X-START:TIME-OFFSET=5,FOO=1\n" + SEGMENT,
        ["FOO=1"],
    ),
    "preload hint unknown attribute": (
        HEADER + '#EXT-X-PRELOAD-HINT:TYPE=PART,URI="p",FOO=1\n' + SEGMENT,
        ["FOO=1"],
    ),
    "map unknown attribute": (
        HEADER + '#EXT-X-MAP:URI="m",FOO=1\n' + SEGMENT,
        ["FOO=1"],
    ),
    "skip unknown attribute": (
        HEADER + "#EXT-X-SKIP:SKIPPED-SEGMENTS=2,FOO=1\n" + SEGMENT,
        ["FOO=1"],
    ),
    "part information unknown attribute": (
        HEADER + "#EXT-X-PART-INF:PART-TARGET=1.5,FOO=1\n" + SEGMENT,
        ["FOO=1"],
    ),
    "server control unknown attribute": (
        HEADER + "#EXT-X-SERVER-CONTROL:CAN-BLOCK-RELOAD=YES,FOO=1\n" + SEGMENT,
        ["FOO=1"],
    ),
    "rendition report unknown attribute": (
        HEADER + SEGMENT + '#EXT-X-RENDITION-REPORT:URI="r.m3u8",FOO=1\n',
        ["FOO=1"],
    ),
    "content steering unknown attribute": (
        HEADER + '#EXT-X-CONTENT-STEERING:SERVER-URI="s",FOO=1\n' + SEGMENT,
        ["FOO=1"],
    ),
    "stream info unknown attributes": (
        '#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=1,FOO=bar,X-VENDOR="a,b"\nv.m3u8\n',
        ["FOO=bar", 'X-VENDOR="a,b"'],
    ),
    "i-frame stream info unknown attribute": (
        VARIANT + '#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=1,URI="i.m3u8",FOO=bar\n',
        ["FOO=bar"],
    ),
    "image stream info unknown attribute": (
        VARIANT
        + '#EXT-X-IMAGE-STREAM-INF:BANDWIDTH=1,RESOLUTION=320x180,URI="i.m3u8",FOO="baz"\n',
        ['FOO="baz"'],
    ),
    "session data unknown attribute": (
        VARIANT + '#EXT-X-SESSION-DATA:DATA-ID="x",VALUE="v",FOO=1\n',
        ["FOO=1"],
    ),
}


@pytest.mark.parametrize(
    "playlist,expected", ROUND_TRIPS.values(), ids=ROUND_TRIPS.keys()
)
def test_attributes_survive_a_round_trip(playlist, expected):
    dumped = m3u8.loads(playlist).dumps()

    for attribute in expected:
        assert attribute in dumped


def test_both_preload_hints_are_kept():
    obj = m3u8.loads(
        HEADER
        + '#EXT-X-PRELOAD-HINT:TYPE=PART,URI="p.m4s"\n'
        + '#EXT-X-PRELOAD-HINT:TYPE=MAP,URI="m.mp4"\n'
        + SEGMENT
    )

    assert [hint.hint_type for hint in obj.preload_hints] == ["PART", "MAP"]
    assert obj.preload_hint is obj.preload_hints[-1]
    assert 'TYPE=PART,URI="p.m4s"' in obj.dumps()
    assert 'TYPE=MAP,URI="m.mp4"' in obj.dumps()


def test_preload_hint_can_be_set_and_cleared():
    obj = m3u8.loads(HEADER + '#EXT-X-PRELOAD-HINT:TYPE=PART,URI="p"\n' + SEGMENT)

    obj.preload_hint = None
    assert obj.preload_hints == []
    assert "PRELOAD-HINT" not in obj.dumps()


def test_preload_hints_follow_base_path():
    obj = m3u8.loads(
        HEADER
        + '#EXT-X-PRELOAD-HINT:TYPE=PART,URI="/x/p.m4s"\n'
        + '#EXT-X-PRELOAD-HINT:TYPE=MAP,URI="/x/m.mp4"\n'
        + SEGMENT
    )

    obj.base_path = "http://cdn/y"

    assert [hint.uri for hint in obj.preload_hints] == [
        "http://cdn/y/p.m4s",
        "http://cdn/y/m.mp4",
    ]


def test_tiles_are_available_on_the_playlist():
    obj = m3u8.loads(
        HEADER + "#EXT-X-TILES:RESOLUTION=320x180,LAYOUT=5x2,DURATION=2.5\n" + SEGMENT
    )

    assert obj.tiles[0].resolution == "320x180"
    assert obj.tiles[0].layout == "5x2"
    assert obj.tiles[0].duration == 2.5


def test_discontinuity_comes_before_the_map():
    dumped = m3u8.loads(
        HEADER + '#EXT-X-DISCONTINUITY\n#EXT-X-MAP:URI="m2"\n' + SEGMENT
    ).dumps()

    assert '#EXT-X-DISCONTINUITY\n#EXT-X-MAP:URI="m2"\n#EXTINF' in dumped
