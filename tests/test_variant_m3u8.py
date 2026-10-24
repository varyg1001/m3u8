# Copyright 2014 Globo.com Player authors. All rights reserved.
# Use of this source code is governed by a MIT License
# license that can be found in the LICENSE file.

import textwrap

import playlists

import m3u8


def test_create_a_variant_m3u8_with_two_playlists():
    variant_m3u8 = m3u8.M3U8()

    subtitles = m3u8.Media(
        "english_sub.m3u8",
        "SUBTITLES",
        "subs",
        "en",
        "English",
        "YES",
        "YES",
        "NO",
        None,
    )
    variant_m3u8.add_media(subtitles)

    low_playlist = m3u8.Playlist(
        "http://example.com/low.m3u8",
        stream_info={
            "bandwidth": 1280000,
            "program_id": 1,
            "closed_captions": "NONE",
            "subtitles": "subs",
        },
        media=[subtitles],
        base_uri=None,
    )
    high_playlist = m3u8.Playlist(
        "http://example.com/high.m3u8",
        stream_info={"bandwidth": 3000000, "program_id": 1, "subtitles": "subs"},
        media=[subtitles],
        base_uri=None,
    )

    variant_m3u8.add_playlist(low_playlist)
    variant_m3u8.add_playlist(high_playlist)

    expected_content = """\
#EXTM3U
#EXT-X-MEDIA:URI="english_sub.m3u8",TYPE=SUBTITLES,GROUP-ID="subs",LANGUAGE="en",NAME="English",DEFAULT=YES,AUTOSELECT=YES,FORCED=NO
#EXT-X-STREAM-INF:PROGRAM-ID=1,CLOSED-CAPTIONS=NONE,BANDWIDTH=1280000,SUBTITLES="subs"
http://example.com/low.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3000000,SUBTITLES="subs"
http://example.com/high.m3u8
"""
    assert expected_content == variant_m3u8.dumps()


def test_create_a_variant_m3u8_with_two_playlists_and_two_iframe_playlists():
    variant_m3u8 = m3u8.M3U8()

    subtitles = m3u8.Media(
        "english_sub.m3u8",
        "SUBTITLES",
        "subs",
        "en",
        "English",
        "YES",
        "YES",
        "NO",
        None,
    )
    variant_m3u8.add_media(subtitles)

    low_playlist = m3u8.Playlist(
        uri="video-800k.m3u8",
        stream_info={
            "bandwidth": 800000,
            "program_id": 1,
            "resolution": "624x352",
            "codecs": "avc1.4d001f, mp4a.40.5",
            "subtitles": "subs",
        },
        media=[subtitles],
        base_uri="http://example.com/",
    )
    high_playlist = m3u8.Playlist(
        uri="video-1200k.m3u8",
        stream_info={
            "bandwidth": 1200000,
            "program_id": 1,
            "codecs": "avc1.4d001f, mp4a.40.5",
            "subtitles": "subs",
        },
        media=[subtitles],
        base_uri="http://example.com/",
    )
    low_iframe_playlist = m3u8.IFramePlaylist(
        uri="video-800k-iframes.m3u8",
        iframe_stream_info={
            "bandwidth": 151288,
            "program_id": 1,
            "closed_captions": None,
            "resolution": "624x352",
            "codecs": "avc1.4d001f",
        },
        base_uri="http://example.com/",
    )
    high_iframe_playlist = m3u8.IFramePlaylist(
        uri="video-1200k-iframes.m3u8",
        iframe_stream_info={"bandwidth": 193350, "codecs": "avc1.4d001f"},
        base_uri="http://example.com/",
    )

    variant_m3u8.add_playlist(low_playlist)
    variant_m3u8.add_playlist(high_playlist)
    variant_m3u8.add_iframe_playlist(low_iframe_playlist)
    variant_m3u8.add_iframe_playlist(high_iframe_playlist)

    expected_content = """\
#EXTM3U
#EXT-X-MEDIA:URI="english_sub.m3u8",TYPE=SUBTITLES,GROUP-ID="subs",\
LANGUAGE="en",NAME="English",DEFAULT=YES,AUTOSELECT=YES,FORCED=NO
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=800000,RESOLUTION=624x352,\
CODECS="avc1.4d001f, mp4a.40.5",SUBTITLES="subs"
video-800k.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1200000,\
CODECS="avc1.4d001f, mp4a.40.5",SUBTITLES="subs"
video-1200k.m3u8
#EXT-X-I-FRAME-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=151288,RESOLUTION=624x352,\
CODECS="avc1.4d001f",URI="video-800k-iframes.m3u8"
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=193350,\
CODECS="avc1.4d001f",URI="video-1200k-iframes.m3u8"
"""
    assert expected_content == variant_m3u8.dumps()


def test_variant_playlist_with_average_bandwidth():
    variant_m3u8 = m3u8.M3U8()

    low_playlist = m3u8.Playlist(
        "http://example.com/low.m3u8",
        stream_info={
            "bandwidth": 1280000,
            "average_bandwidth": 1257891,
            "program_id": 1,
            "subtitles": "subs",
        },
        media=[],
        base_uri=None,
    )
    high_playlist = m3u8.Playlist(
        "http://example.com/high.m3u8",
        stream_info={
            "bandwidth": 3000000,
            "average_bandwidth": 2857123,
            "program_id": 1,
            "subtitles": "subs",
        },
        media=[],
        base_uri=None,
    )

    variant_m3u8.add_playlist(low_playlist)
    variant_m3u8.add_playlist(high_playlist)

    expected_content = """\
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1280000,AVERAGE-BANDWIDTH=1257891
http://example.com/low.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3000000,AVERAGE-BANDWIDTH=2857123
http://example.com/high.m3u8
"""
    assert expected_content == variant_m3u8.dumps()


def test_variant_playlist_with_video_range():
    variant_m3u8 = m3u8.M3U8()

    sdr_playlist = m3u8.Playlist(
        "http://example.com/sdr.m3u8",
        stream_info={"bandwidth": 1280000, "video_range": "SDR", "program_id": 1},
        media=[],
        base_uri=None,
    )
    hdr_playlist = m3u8.Playlist(
        "http://example.com/hdr.m3u8",
        stream_info={"bandwidth": 3000000, "video_range": "PQ", "program_id": 1},
        media=[],
        base_uri=None,
    )

    variant_m3u8.add_playlist(sdr_playlist)
    variant_m3u8.add_playlist(hdr_playlist)

    expected_content = """\
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1280000,VIDEO-RANGE=SDR
http://example.com/sdr.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3000000,VIDEO-RANGE=PQ
http://example.com/hdr.m3u8
"""
    assert expected_content == variant_m3u8.dumps()


def test_variant_playlist_with_hdcp_level():
    variant_m3u8 = m3u8.M3U8()

    none_playlist = m3u8.Playlist(
        "http://example.com/none.m3u8",
        stream_info={"bandwidth": 1280000, "hdcp_level": "NONE", "program_id": 1},
        media=[],
        base_uri=None,
    )
    type0_playlist = m3u8.Playlist(
        "http://example.com/type0.m3u8",
        stream_info={"bandwidth": 3000000, "hdcp_level": "TYPE-0", "program_id": 1},
        media=[],
        base_uri=None,
    )
    type1_playlist = m3u8.Playlist(
        "http://example.com/type1.m3u8",
        stream_info={"bandwidth": 4000000, "hdcp_level": "TYPE-1", "program_id": 1},
        media=[],
        base_uri=None,
    )

    variant_m3u8.add_playlist(none_playlist)
    variant_m3u8.add_playlist(type0_playlist)
    variant_m3u8.add_playlist(type1_playlist)

    expected_content = """\
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1280000,HDCP-LEVEL=NONE
http://example.com/none.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3000000,HDCP-LEVEL=TYPE-0
http://example.com/type0.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=4000000,HDCP-LEVEL=TYPE-1
http://example.com/type1.m3u8
"""
    assert expected_content == variant_m3u8.dumps()


def test_variant_playlist_with_multiple_media():
    variant_m3u8 = m3u8.loads(playlists.MULTI_MEDIA_PLAYLIST)
    assert variant_m3u8.dumps() == playlists.MULTI_MEDIA_PLAYLIST


def test_create_a_variant_m3u8_with_iframe_with_average_bandwidth_playlists():
    variant_m3u8 = m3u8.M3U8()

    subtitles = m3u8.Media(
        "english_sub.m3u8",
        "SUBTITLES",
        "subs",
        "en",
        "English",
        "YES",
        "YES",
        "NO",
        None,
    )
    variant_m3u8.add_media(subtitles)

    low_playlist = m3u8.Playlist(
        uri="video-800k.m3u8",
        stream_info={
            "bandwidth": 800000,
            "average_bandwidth": 555000,
            "resolution": "624x352",
            "codecs": "avc1.4d001f, mp4a.40.5",
            "subtitles": "subs",
        },
        media=[subtitles],
        base_uri="http://example.com/",
    )
    low_iframe_playlist = m3u8.IFramePlaylist(
        uri="video-800k-iframes.m3u8",
        iframe_stream_info={
            "bandwidth": 151288,
            "average_bandwidth": 111000,
            "resolution": "624x352",
            "codecs": "avc1.4d001f",
        },
        base_uri="http://example.com/",
    )

    variant_m3u8.add_playlist(low_playlist)
    variant_m3u8.add_iframe_playlist(low_iframe_playlist)

    expected_content = """\
#EXTM3U
#EXT-X-MEDIA:URI="english_sub.m3u8",TYPE=SUBTITLES,GROUP-ID="subs",\
LANGUAGE="en",NAME="English",DEFAULT=YES,AUTOSELECT=YES,FORCED=NO
#EXT-X-STREAM-INF:BANDWIDTH=800000,AVERAGE-BANDWIDTH=555000,\
RESOLUTION=624x352,CODECS="avc1.4d001f, mp4a.40.5",SUBTITLES="subs"
video-800k.m3u8
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=151288,\
AVERAGE-BANDWIDTH=111000,RESOLUTION=624x352,CODECS="avc1.4d001f",\
URI="video-800k-iframes.m3u8"
"""
    assert expected_content == variant_m3u8.dumps()


def test_create_a_variant_m3u8_with_iframe_with_video_range_playlists():
    variant_m3u8 = m3u8.M3U8()

    for vrange in ["SDR", "PQ", "HLG"]:
        playlist = m3u8.Playlist(
            uri="video-%s.m3u8" % vrange,
            stream_info={"bandwidth": 3000000, "video_range": vrange},
            media=[],
            base_uri="http://example.com/%s" % vrange,
        )
        iframe_playlist = m3u8.IFramePlaylist(
            uri="video-%s-iframes.m3u8" % vrange,
            iframe_stream_info={"bandwidth": 3000000, "video_range": vrange},
            base_uri="http://example.com/%s" % vrange,
        )

        variant_m3u8.add_playlist(playlist)
        variant_m3u8.add_iframe_playlist(iframe_playlist)

    expected_content = """\
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=3000000,VIDEO-RANGE=SDR
video-SDR.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=3000000,VIDEO-RANGE=PQ
video-PQ.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=3000000,VIDEO-RANGE=HLG
video-HLG.m3u8
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=3000000,VIDEO-RANGE=SDR,URI="video-SDR-iframes.m3u8"
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=3000000,VIDEO-RANGE=PQ,URI="video-PQ-iframes.m3u8"
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=3000000,VIDEO-RANGE=HLG,URI="video-HLG-iframes.m3u8"
"""
    assert expected_content == variant_m3u8.dumps()


def test_create_a_variant_m3u8_with_iframe_with_hdcp_level_playlists():
    variant_m3u8 = m3u8.M3U8()

    for hdcplv in ["NONE", "TYPE-0", "TYPE-1"]:
        playlist = m3u8.Playlist(
            uri="video-%s.m3u8" % hdcplv,
            stream_info={"bandwidth": 3000000, "hdcp_level": hdcplv},
            media=[],
            base_uri="http://example.com/%s" % hdcplv,
        )
        iframe_playlist = m3u8.IFramePlaylist(
            uri="video-%s-iframes.m3u8" % hdcplv,
            iframe_stream_info={"bandwidth": 3000000, "hdcp_level": hdcplv},
            base_uri="http://example.com/%s" % hdcplv,
        )

        variant_m3u8.add_playlist(playlist)
        variant_m3u8.add_iframe_playlist(iframe_playlist)

    expected_content = """\
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=3000000,HDCP-LEVEL=NONE
video-NONE.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=3000000,HDCP-LEVEL=TYPE-0
video-TYPE-0.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=3000000,HDCP-LEVEL=TYPE-1
video-TYPE-1.m3u8
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=3000000,HDCP-LEVEL=NONE,URI="video-NONE-iframes.m3u8"
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=3000000,HDCP-LEVEL=TYPE-0,URI="video-TYPE-0-iframes.m3u8"
#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=3000000,HDCP-LEVEL=TYPE-1,URI="video-TYPE-1-iframes.m3u8"
"""
    assert expected_content == variant_m3u8.dumps()


def test_create_a_variant_m3u8_with_two_playlists_and_two_image_playlists():
    variant_m3u8 = m3u8.M3U8()

    subtitles = m3u8.Media(
        "english_sub.m3u8",
        "SUBTITLES",
        "subs",
        "en",
        "English",
        "YES",
        "YES",
        "NO",
        None,
    )
    variant_m3u8.add_media(subtitles)

    low_playlist = m3u8.Playlist(
        uri="video-800k.m3u8",
        stream_info={
            "bandwidth": 800000,
            "program_id": 1,
            "resolution": "624x352",
            "codecs": "avc1.4d001f, mp4a.40.5",
            "subtitles": "subs",
        },
        media=[subtitles],
        base_uri="http://example.com/",
    )
    high_playlist = m3u8.Playlist(
        uri="video-1200k.m3u8",
        stream_info={
            "bandwidth": 1200000,
            "program_id": 1,
            "codecs": "avc1.4d001f, mp4a.40.5",
            "subtitles": "subs",
        },
        media=[subtitles],
        base_uri="http://example.com/",
    )
    low_image_playlist = m3u8.ImagePlaylist(
        uri="thumbnails-sd.m3u8",
        image_stream_info={
            "bandwidth": 151288,
            "resolution": "320x160",
            "codecs": "jpeg",
        },
        base_uri="http://example.com/",
    )
    high_image_playlist = m3u8.ImagePlaylist(
        uri="thumbnails-hd.m3u8",
        image_stream_info={
            "bandwidth": 193350,
            "resolution": "640x320",
            "codecs": "jpeg",
        },
        base_uri="http://example.com/",
    )

    variant_m3u8.add_playlist(low_playlist)
    variant_m3u8.add_playlist(high_playlist)
    variant_m3u8.add_image_playlist(low_image_playlist)
    variant_m3u8.add_image_playlist(high_image_playlist)

    expected_content = """\
#EXTM3U
#EXT-X-MEDIA:URI="english_sub.m3u8",TYPE=SUBTITLES,GROUP-ID="subs",\
LANGUAGE="en",NAME="English",DEFAULT=YES,AUTOSELECT=YES,FORCED=NO
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=800000,RESOLUTION=624x352,\
CODECS="avc1.4d001f, mp4a.40.5",SUBTITLES="subs"
video-800k.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1200000,\
CODECS="avc1.4d001f, mp4a.40.5",SUBTITLES="subs"
video-1200k.m3u8
#EXT-X-IMAGE-STREAM-INF:BANDWIDTH=151288,RESOLUTION=320x160,\
CODECS="jpeg",URI="thumbnails-sd.m3u8"
#EXT-X-IMAGE-STREAM-INF:BANDWIDTH=193350,RESOLUTION=640x320,\
CODECS="jpeg",URI="thumbnails-hd.m3u8"
"""
    assert expected_content == variant_m3u8.dumps()


def test_score_and_allowed_cpc_round_trip():
    playlist = textwrap.dedent(
        """\
        #EXTM3U
        #EXT-X-STREAM-INF:BANDWIDTH=1000,SCORE=2.5,ALLOWED-CPC="com.example.drm1:SMART-TV/PC,com.example.drm2:HW"
        video.m3u8
        """
    )
    obj = m3u8.loads(playlist)
    stream_info = obj.playlists[0].stream_info

    assert stream_info.score == 2.5
    assert stream_info.allowed_cpc == "com.example.drm1:SMART-TV/PC,com.example.drm2:HW"
    assert obj.dumps().strip() == playlist.strip()


def test_i_frame_stream_inf_keeps_attributes_added_in_rfc8216bis():
    playlist = textwrap.dedent(
        """\
        #EXTM3U
        #EXT-X-STREAM-INF:BANDWIDTH=1000
        video.m3u8
        #EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=1000,URI="iframe.m3u8",SUPPLEMENTAL-CODECS="dvh1.05",REQ-VIDEO-LAYOUT="CH-STEREO",SCORE=1.5,ALLOWED-CPC="com.example.drm1:HW"
        """
    )
    obj = m3u8.loads(playlist)
    stream_info = obj.iframe_playlists[0].iframe_stream_info

    assert stream_info.supplemental_codecs == "dvh1.05"
    assert stream_info.req_video_layout == "CH-STEREO"
    assert stream_info.score == 1.5
    assert stream_info.allowed_cpc == "com.example.drm1:HW"
    dumped = obj.dumps()
    for attribute in (
        'SUPPLEMENTAL-CODECS="dvh1.05"',
        'REQ-VIDEO-LAYOUT="CH-STEREO"',
        "SCORE=1.5",
        'ALLOWED-CPC="com.example.drm1:HW"',
    ):
        assert attribute in dumped


def test_media_bit_depth_and_sample_rate_round_trip():
    playlist = textwrap.dedent(
        """\
        #EXTM3U
        #EXT-X-STREAM-INF:BANDWIDTH=1000
        video.m3u8
        #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="lossless",NAME="en",URI="audio.m3u8",BIT-DEPTH=24,SAMPLE-RATE=48000
        """
    )
    obj = m3u8.loads(playlist)

    assert obj.media[0].bit_depth == 24
    assert obj.media[0].sample_rate == 48000
    assert "BIT-DEPTH=24,SAMPLE-RATE=48000" in obj.dumps()
