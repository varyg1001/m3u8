import pytest

import m3u8
from m3u8.model import Key, Segment

PLAYLIST = """\
#EXTM3U
#EXT-X-TARGETDURATION:5
#EXT-X-KEY:METHOD=AES-128,URI="key.bin"
#EXTINF:5,
a.ts
#EXTINF:5,
b.ts
"""
URI = "http://example.com/dir/playlist.m3u8"


def test_repr_of_the_playlist_is_short_and_says_where_it_comes_from():
    assert repr(m3u8.loads(PLAYLIST)) == "M3U8(segments=2, playlists=0)"
    assert (
        repr(m3u8.loads(PLAYLIST, uri=URI))
        == f"M3U8(segments=2, playlists=0, uri='{URI}')"
    )


def test_repr_of_a_tag_is_its_line():
    obj = m3u8.loads(PLAYLIST)

    assert repr(obj.keys[0]) == "Key('#EXT-X-KEY:METHOD=AES-128,URI=\"key.bin\"')"
    assert repr(obj.segments) == repr(list(obj.segments))
    assert "b.ts" in repr(obj.segments[1])


def test_repr_never_raises():
    broken = Segment(uri="a.ts", duration="not a number")

    assert repr(broken).startswith("<m3u8.model.Segment object at")


def test_copy_shares_nothing_with_the_original():
    obj = m3u8.loads(PLAYLIST, uri=URI)

    clone = obj.copy()
    clone.segments[0].uri = "changed.ts"
    clone.keys[0].uri = "changed.bin"
    clone.segments.append(Segment(uri="c.ts", duration=5))

    assert obj.dumps() == m3u8.loads(PLAYLIST, uri=URI).dumps()
    assert clone.dumps() != obj.dumps()
    assert clone.uri == URI


def test_copy_of_a_segment_and_a_key():
    segment = m3u8.loads(PLAYLIST).segments[0]
    key = segment.key

    segment_clone = segment.copy()
    key_clone = key.copy()
    segment_clone.uri = "changed.ts"
    key_clone.uri = "changed.bin"

    assert segment.uri == "a.ts"
    assert key.uri == "key.bin"
    assert key_clone == Key("AES-128", None, uri="changed.bin")


def test_objects_keep_identity_equality_and_stay_hashable():
    segment = m3u8.loads(PLAYLIST).segments[0]

    assert segment != segment.copy()
    assert len({segment, segment.copy()}) == 2


def test_files_are_listed_as_written_and_absolute_files_resolved():
    obj = m3u8.loads(PLAYLIST, uri=URI)

    assert obj.files == ["key.bin", "a.ts", "b.ts"]
    assert obj.absolute_files == [
        "http://example.com/dir/key.bin",
        "http://example.com/dir/a.ts",
        "http://example.com/dir/b.ts",
    ]


def test_absolute_files_need_a_base_uri_for_relative_files():
    with pytest.raises(ValueError, match="base_uri"):
        m3u8.loads(PLAYLIST).absolute_files  # noqa: B018


def test_absolute_files_of_absolute_uris_need_no_base_uri():
    obj = m3u8.loads(
        PLAYLIST.replace("a.ts", "http://cdn/a.ts")
        .replace("b.ts", "http://cdn/b.ts")
        .replace("key.bin", "http://cdn/key.bin")
    )

    assert obj.absolute_files == obj.files
