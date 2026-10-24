# Copyright 2014 Globo.com Player authors. All rights reserved.
# Use of this source code is governed by a MIT License
# license that can be found in the LICENSE file.

import invalid_versioned_playlists
import pytest

import m3u8
import m3u8.version_matching_rules
from m3u8 import ParseError

VALID = "#EXTM3U\n#EXT-X-TARGETDURATION:5\n#EXTINF:5,\na.ts\n"
# floating-point durations need protocol version 3
VALID_V3 = VALID.replace(
    "#EXT-X-TARGETDURATION", "#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION"
)


def test_valid_playlist_passes_strict_mode():
    assert m3u8.M3U8(VALID, strict=True).segments[0].uri == "a.ts"


def test_should_fail_if_first_line_not_EXTM3U():
    with pytest.raises(ParseError) as error:
        m3u8.M3U8("#EXT-X-TARGETDURATION:5\n#EXTINF:5,\na.ts\n", strict=True)

    assert error.value.lineno == 1


def test_byte_order_mark_before_EXTM3U_is_accepted():
    assert m3u8.M3U8("\ufeff" + VALID, strict=True).segments[0].uri == "a.ts"


def test_comments_are_accepted():
    playlist = VALID.replace("#EXTINF", "# a comment\n#EXTINF")

    assert m3u8.M3U8(playlist, strict=True).segments[0].uri == "a.ts"


def test_unknown_tags_are_rejected():
    with pytest.raises(ParseError):
        m3u8.M3U8(VALID.replace("#EXTINF", "#EXT-X-UNKNOWN:1\n#EXTINF"), strict=True)


@pytest.mark.xfail
def test_should_fail_if_expected_ts_segment_line_is_not_valid():
    assert 0


@pytest.mark.xfail
def test_should_fail_if_EXT_X_MEDIA_SEQUENCE_is_diffent_from_sequence_number_of_first_uri():
    assert 0


def test_should_fail_if_more_than_one_EXT_X_MEDIA_SEQUENCE():
    playlist = VALID.replace("#EXTINF", "#EXT-X-MEDIA-SEQUENCE:1\n" * 2 + "#EXTINF")

    with pytest.raises(ParseError):
        m3u8.M3U8(playlist, strict=True)


def test_should_fail_if_EXT_X_MEDIA_SEQUENCE_is_not_a_number():
    playlist = VALID.replace("#EXTINF", "#EXT-X-MEDIA-SEQUENCE:x\n#EXTINF")

    with pytest.raises(ParseError):
        m3u8.M3U8(playlist, strict=True)


def test_should_validate_supported_EXT_X_VERSION():
    with pytest.raises(Exception):  # noqa: B017
        m3u8.parse(invalid_versioned_playlists.M3U8_RULE_IV, strict=True)


def test_should_fail_if_any_EXTINF_duration_is_greater_than_TARGET_DURATION():
    with pytest.raises(ParseError):
        m3u8.M3U8(VALID_V3.replace("EXTINF:5", "EXTINF:6.5"), strict=True)


def test_EXTINF_duration_is_compared_rounded_to_the_TARGET_DURATION():
    assert m3u8.M3U8(VALID_V3.replace("EXTINF:5", "EXTINF:5.4"), strict=True)


def test_should_fail_if_TARGET_DURATION_not_found():
    with pytest.raises(ParseError):
        m3u8.M3U8(VALID.replace("#EXT-X-TARGETDURATION:5\n", ""), strict=True)


@pytest.mark.xfail
def test_should_fail_if_invalid_m3u8_url_after_EXT_X_STREAM_INF():
    assert 0
