# Changelog

## 7.0.0

The changes follow [draft-pantos-hls-rfc8216bis-22](https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis-22),
the HLS specification (protocol version 13).

### Breaking changes

- **Python 3.11 to 3.14.** Python 3.9 and 3.10 are not supported anymore. The
  `backports-datetime-fromisoformat` dependency is gone, m3u8 has no required
  dependencies.
- **The build uses `pyproject.toml` and uv.** `setup.py` and the requirements
  files are removed, use `uv sync` for a development environment.
- **Some parsed attributes lost their quotes.** `supplemental_codecs`,
  `characteristics` and `req_video_layout` of the stream info were returned
  with the quotes of the playlist (`'"CH-STEREO"'`), and written back with
  doubled quotes. They are `'CH-STEREO'` now like the other quoted attributes.
- **Strict mode checks more.** It requires `#EXTM3U` as the first line, one
  `EXT-X-MEDIA-SEQUENCE`, an `EXT-X-TARGETDURATION` in a Media Playlist and
  segments that are not longer than it (rounded). A playlist without
  `EXT-X-VERSION` is checked as version 1, and the version rules cover the
  versions 5 to 13. Plain `#` comments are accepted. A playlist that passed
  before can raise now.
- **Malformed tags raise `ParseError`** with the line, instead of a bare
  `ValueError`, `KeyError` or `IndexError`. `ParseError` is a `ValueError`, so
  `except ValueError` still works.
- **Tags are matched exactly.** `#EXT-X-KEYFRAME` was parsed as `EXT-X-KEY`,
  now it is an unknown tag and ignored.
- **`Segment.key` is a property** for the last of the new `Segment.keys`.
  Assigning it still works.
- **`EXT-X-DISCONTINUITY` is written before `EXT-X-MAP`,** it was after it.
- **Unknown attributes of `EXT-X-KEY` keep their quotes** in `Key`'s
  `_extra_params`.
- **`DefaultHTTPClient` keeps cookies** between the downloads of a client.
  Custom headers are still only sent to the requested host.
- **`M3U8.__unicode__` is removed,** use `str()`.

### Added

- `EXT-X-DEFINE`: variable references are replaced while parsing, `M3U8.defines`
  and `M3U8.variables`, and `imports=` for the variables of a Multivariant
  Playlist. `QUERYPARAM` reads the query of the playlist `uri`.
- Several `EXT-X-KEY` tags for a segment (`Segment.keys`), for example one per
  DRM system.
- `SCORE` and `ALLOWED-CPC` of `EXT-X-STREAM-INF` and `EXT-X-I-FRAME-STREAM-INF`,
  `BIT-DEPTH` and `SAMPLE-RATE` of `EXT-X-MEDIA`.
- The attributes of IPTV playlists in `EXTINF`: `Segment.extinf_attributes`.
- The protocol version rules of the specification for the versions 5 to 13.
- `NiquestsHTTPClient` with `pip install m3u8[niquests]`, `strict=` for `load`
  and `loads`, and `M3U8.uri`.
- `M3U8.preload_hints` (a PART and a MAP hint), `M3U8.tiles`,
  `M3U8.absolute_files`, `copy()` and a readable `repr()` for the model.

### Fixed

- A parsed playlist keeps more when it is written again: zero values
  (`DURATION=0`, `HOLD-BACK=0`, `EXT-X-BITRATE:0`), an empty `SESSION-DATA`
  value, and the unknown attributes of tags that raised `TypeError` or dropped
  them. `SUPPLEMENTAL-CODECS` was written from `CODECS` and
  `REQ-VIDEO-LAYOUT` with an underscore.
- `EXT-X-CUE-OUT-CONT` keeps its `SCTE35` value when it has no duration.
- `DateRange` dates given as `datetime` are written in the ISO 8601 form.
- The `base_path` setter replaced every occurrence of the old path and did
  not ignore a `/` in the fragment of a URI.
- Program date times were shifted by the parts of a low latency segment.
- `Key` and `InitializationSection` are hashable, keys that differ only by
  `KEYFORMAT` are not merged, an unencrypted segment after an encrypted one
  is written as `METHOD=NONE` instead of `None`.
- `EXT-X-VERSION:3.0` and `EXT-X-TARGETDURATION:6.0` are accepted.
- A byte order mark is ignored, only CR, LF and CRLF end a line, and a title
  that contains `#EXTINF:` is not changed.
- `M3U8.files` is computed when it is read, so it follows `base_path`. It can
  still be assigned.
- `str(M3U8)` returns the playlist, and `load` has no mutable default
  arguments.
- The response of `DefaultHTTPClient` is closed, and `gzip`, `x-gzip` and
  `deflate` are read regardless of case.
