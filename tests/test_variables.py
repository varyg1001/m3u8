import textwrap

import pytest

import m3u8
from m3u8.parser import ParseError

MEDIA_PLAYLIST = textwrap.dedent(
    """\
    #EXTM3U
    #EXT-X-VERSION:8
    #EXT-X-TARGETDURATION:5
    #EXT-X-DEFINE:NAME="cdn",VALUE="https://cdn.example.com/v1"
    #EXT-X-DEFINE:NAME="iv",VALUE="00112233445566778899aabbccddeeff"
    #EXT-X-KEY:METHOD=AES-128,URI="{$cdn}/key.bin",IV=0x{$iv}
    #EXTINF:5,
    {$cdn}/a.ts
    #EXTINF:5,
    {$cdn}/b.ts
    """
)


def test_variables_are_replaced_in_uris_and_quoted_values():
    obj = m3u8.loads(MEDIA_PLAYLIST)

    assert obj.variables == {
        "cdn": "https://cdn.example.com/v1",
        "iv": "00112233445566778899aabbccddeeff",
    }
    assert obj.segments[0].uri == "https://cdn.example.com/v1/a.ts"
    assert obj.segments[1].uri == "https://cdn.example.com/v1/b.ts"
    assert obj.keys[0].uri == "https://cdn.example.com/v1/key.bin"
    assert obj.keys[0].iv == "0x00112233445566778899aabbccddeeff"


def test_define_tags_are_kept_and_dumped():
    obj = m3u8.loads(MEDIA_PLAYLIST)

    assert [(d.name, d.value) for d in obj.defines] == [
        ("cdn", "https://cdn.example.com/v1"),
        ("iv", "00112233445566778899aabbccddeeff"),
    ]
    dumped = obj.dumps()
    assert '#EXT-X-DEFINE:NAME="cdn",VALUE="https://cdn.example.com/v1"' in dumped
    assert "https://cdn.example.com/v1/a.ts" in dumped
    assert "{$" not in dumped


def test_reference_in_unquoted_attribute_is_not_replaced():
    obj = m3u8.loads(
        textwrap.dedent(
            """\
            #EXTM3U
            #EXT-X-DEFINE:NAME="r",VALUE="PQ"
            #EXT-X-STREAM-INF:BANDWIDTH=1,HDCP-LEVEL={$r},CODECS="{$r}"
            video.m3u8
            """
        )
    )

    stream_info = obj.playlists[0].stream_info
    assert stream_info.hdcp_level == "{$r}"
    assert stream_info.codecs == "PQ"


def test_import_comes_from_the_multivariant_playlist_variables():
    master = m3u8.loads(
        textwrap.dedent(
            """\
            #EXTM3U
            #EXT-X-DEFINE:NAME="token",VALUE="abc"
            #EXT-X-STREAM-INF:BANDWIDTH=1000
            video.m3u8?t={$token}
            """
        )
    )
    media = m3u8.loads(
        textwrap.dedent(
            """\
            #EXTM3U
            #EXT-X-DEFINE:IMPORT="token"
            #EXTINF:5,
            seg.ts?t={$token}
            """
        ),
        imports=master.variables,
    )

    assert master.playlists[0].uri == "video.m3u8?t=abc"
    assert media.segments[0].uri == "seg.ts?t=abc"
    assert 'IMPORT="token"' in media.dumps()


def test_queryparam_comes_from_the_playlist_uri_and_is_percent_decoded():
    obj = m3u8.loads(
        textwrap.dedent(
            """\
            #EXTM3U
            #EXT-X-DEFINE:QUERYPARAM="sig"
            #EXTINF:5,
            seg.ts?sig={$sig}
            """
        ),
        uri="https://example.com/media.m3u8?other=1&sig=a%2Fb+c",
    )

    assert obj.variables == {"sig": "a/b+c"}
    assert obj.segments[0].uri == "seg.ts?sig=a/b+c"
    assert 'QUERYPARAM="sig"' in obj.dumps()


def test_unresolved_reference_is_left_alone_unless_strict():
    content = "#EXTM3U\n#EXTINF:5,\n{$missing}/a.ts\n"

    assert m3u8.loads(content).segments[0].uri == "{$missing}/a.ts"
    with pytest.raises(ParseError):
        m3u8.M3U8(content, strict=True)


@pytest.mark.parametrize(
    "define",
    [
        '#EXT-X-DEFINE:NAME="bad name",VALUE="x"',
        '#EXT-X-DEFINE:NAME="novalue"',
        '#EXT-X-DEFINE:IMPORT="unknown"',
        '#EXT-X-DEFINE:QUERYPARAM="unknown"',
        '#EXT-X-DEFINE:NAME="a",VALUE="1"\n#EXT-X-DEFINE:NAME="a",VALUE="2"',
    ],
)
def test_invalid_define_raises_in_strict_mode(define):
    content = f"#EXTM3U\n{define}\n#EXTINF:5,\na.ts\n"

    with pytest.raises(ParseError):
        m3u8.M3U8(content, strict=True)
    m3u8.loads(content)  # not strict: no exception
