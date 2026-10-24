![image](https://github.com/globocom/m3u8/actions/workflows/main.yml/badge.svg) [![image](https://badge.fury.io/py/m3u8.svg)](https://badge.fury.io/py/m3u8)

# m3u8

Python [m3u8](https://tools.ietf.org/html/rfc8216) parser.

# Documentation

## Loading a playlist

To load a playlist into an object from uri, file path or directly from
string, use the `load/loads` functions:

```python
import m3u8

playlist = m3u8.load('http://videoserver.com/playlist.m3u8')  # this could also be an absolute filename
print(playlist.segments)
print(playlist.target_duration)

# if you already have the content as string, use

playlist = m3u8.loads('#EXTM3U8 ... etc ... ')
```

## Dumping a playlist

To dump a playlist from an object to the console or a file, use the
`dump/dumps` functions:

``` python
import m3u8

playlist = m3u8.load('http://videoserver.com/playlist.m3u8')
print(playlist.dumps())

# if you want to write a file from its content

playlist.dump('playlist.m3u8')
```

## Using another HTTP client

`m3u8.load` downloads playlists with `urllib`, so the library needs no
dependencies. To use something else, for example for HTTP/2, retries or a
session with cookies, pass any object with a `download` method that returns the
content and the base URI of the playlist:

``` python
from urllib.parse import urljoin

import m3u8
import niquests  # or requests


class Client:
    def __init__(self):
        self.session = niquests.Session()

    def download(self, uri, timeout=None, headers=None, verify_ssl=True):
        response = self.session.get(
            uri, timeout=timeout, headers=headers, verify=verify_ssl
        )
        response.raise_for_status()
        return response.text, urljoin(response.url, ".")


playlist = m3u8.load("http://videoserver.com/playlist.m3u8", http_client=Client())
```

The default client, `m3u8.httpclient.DefaultHTTPClient`, takes `proxies` and a
`cookie_jar` that keeps the cookies between downloads.

A client that uses niquests is included, install it with
`pip install m3u8[niquests]`. It takes the `session` to use and `proxies`:

``` python
import m3u8
from m3u8.httpclient import NiquestsHTTPClient

playlist = m3u8.load(
    "http://videoserver.com/playlist.m3u8", http_client=NiquestsHTTPClient()
)
```

## Strict mode

`m3u8.load`, `m3u8.loads` and `m3u8.M3U8` take `strict=True` to raise a
`ParseError` (a `ValueError`) for what the specification forbids, for example a
missing `#EXTM3U`, an unknown tag or a tag that needs a higher
`#EXT-X-VERSION` than the one the playlist declares.

# Supported tags

-   [\#EXT-X-TARGETDURATION](https://tools.ietf.org/html/rfc8216#section-4.3.3.1)
-   [\#EXT-X-MEDIA-SEQUENCE](https://tools.ietf.org/html/rfc8216#section-4.3.3.2)
-   [\#EXT-X-DISCONTINUITY-SEQUENCE](https://tools.ietf.org/html/rfc8216#section-4.3.3.3)
-   [\#EXT-X-PROGRAM-DATE-TIME](https://tools.ietf.org/html/rfc8216#section-4.3.2.6)
-   [\#EXT-X-MEDIA](https://tools.ietf.org/html/rfc8216#section-4.3.4.1)
-   [\#EXT-X-PLAYLIST-TYPE](https://tools.ietf.org/html/rfc8216#section-4.3.3.5)
-   [\#EXT-X-KEY](https://tools.ietf.org/html/rfc8216#section-4.3.2.4)
-   [\#EXT-X-STREAM-INF](https://tools.ietf.org/html/rfc8216#section-4.3.4.2)
-   [\#EXT-X-VERSION](https://tools.ietf.org/html/rfc8216#section-4.3.1.2)
-   [\#EXT-X-ALLOW-CACHE](https://datatracker.ietf.org/doc/html/draft-pantos-http-live-streaming-07#section-3.3.6)
-   [\#EXT-X-ENDLIST](https://tools.ietf.org/html/rfc8216#section-4.3.3.4)
-   [\#EXTINF](https://tools.ietf.org/html/rfc8216#section-4.3.2.1)
-   [\#EXT-X-I-FRAMES-ONLY](https://tools.ietf.org/html/rfc8216#section-4.3.3.6)
-   [\#EXT-X-BITRATE](https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis#section-4.4.4.8)
-   [\#EXT-X-BYTERANGE](https://tools.ietf.org/html/rfc8216#section-4.3.2.2)
-   [\#EXT-X-I-FRAME-STREAM-INF](https://tools.ietf.org/html/rfc8216#section-4.3.4.3)
-   [\#EXT-X-IMAGES-ONLY](https://github.com/image-media-playlist/spec/blob/master/image_media_playlist_v0_4.pdf)
-   [\#EXT-X-IMAGE-STREAM-INF](https://github.com/image-media-playlist/spec/blob/master/image_media_playlist_v0_4.pdf)
-   [\#EXT-X-TILES](https://github.com/image-media-playlist/spec/blob/master/image_media_playlist_v0_4.pdf)
-   [\#EXT-X-DISCONTINUITY](https://tools.ietf.org/html/rfc8216#section-4.3.2.3)
-   \#EXT-X-CUE-OUT
-   \#EXT-X-CUE-OUT-CONT
-   \#EXT-X-CUE-IN
-   \#EXT-X-CUE-SPAN
-   \#EXT-OATCLS-SCTE35
-   [\#EXT-X-INDEPENDENT-SEGMENTS](https://tools.ietf.org/html/rfc8216#section-4.3.5.1)
-   [\#EXT-X-MAP](https://tools.ietf.org/html/rfc8216#section-4.3.2.5)
-   [\#EXT-X-START](https://tools.ietf.org/html/rfc8216#section-4.3.5.2)
-   [\#EXT-X-SERVER-CONTROL](https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis#section-4.4.3.8)
-   [\#EXT-X-PART-INF](https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis#section-4.4.3.7)
-   [\#EXT-X-PART](https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis#section-4.4.4.9)
-   [\#EXT-X-RENDITION-REPORT](https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis#section-4.4.5.4)
-   [\#EXT-X-SKIP](https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis#section-4.4.5.2)
-   [\#EXT-X-SESSION-DATA](https://tools.ietf.org/html/rfc8216#section-4.3.4.4)
-   [\#EXT-X-PRELOAD-HINT](https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis-09#section-4.4.5.3)
-   [\#EXT-X-SESSION-KEY](https://tools.ietf.org/html/rfc8216#section-4.3.4.5)
-   [\#EXT-X-DATERANGE](https://tools.ietf.org/html/rfc8216#section-4.3.2.7)
-   [\#EXT-X-GAP](https://tools.ietf.org/html/draft-pantos-hls-rfc8216bis-05#section-4.4.2.7)
-   [\#EXT-X-CONTENT-STEERING](https://tools.ietf.org/html/draft-pantos-hls-rfc8216bis-10#section-4.4.6.64)
-   [\#EXT-X-DEFINE](https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis#section-4.4.2.3)

# Frequently Asked Questions

-   [FAQ](https://github.com/globocom/m3u8/wiki/FAQ)

# Running Tests

The project uses [uv](https://docs.astral.sh/uv/). The script installs the
development dependencies, starts the test server and runs the tests:

``` bash
$ ./runtests
```

To set up an environment only, run `uv sync`.

# Contributing

All contributions are welcome, but we will merge a pull request if, and
only if, it

- Has tests
- Follows the code conventions

If you plan to implement a new feature or something that will take more
than a few minutes, please open an issue to make sure we don't work on
the same thing.
