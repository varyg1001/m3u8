import gzip
import unittest
import urllib.request
import zlib
from http.client import HTTPResponse
from http.cookiejar import CookieJar
from unittest.mock import Mock, patch

from m3u8.httpclient import DefaultHTTPClient


class MockHeaders:
    def __init__(self, encoding=None):
        self.encoding = encoding

    def get_content_charset(self, failobj="utf-8"):
        return self.encoding or failobj


class TestDefaultHTTPClient(unittest.TestCase):
    @patch("urllib.request.OpenerDirector.open")
    def test_download_normal_content(self, mock_open):
        client = DefaultHTTPClient()
        mock_response = Mock(spec=HTTPResponse)
        mock_response.read.return_value = b"playlist content"
        mock_response.info.return_value = {}
        mock_response.geturl.return_value = "http://example.com/index.m3u8"
        mock_response.headers = MockHeaders()
        mock_open.return_value = mock_response

        content, base_uri = client.download("http://example.com/index.m3u8")

        self.assertEqual(content, "playlist content")
        self.assertEqual(base_uri, "http://example.com/")

    @patch("urllib.request.OpenerDirector.open")
    def test_download_gzipped_content(self, mock_open):
        client = DefaultHTTPClient()
        original_content = "playlist gzipped content"
        gzipped_content = gzip.compress(original_content.encode("utf-8"))
        mock_response = Mock(spec=HTTPResponse)
        mock_response.read.return_value = gzipped_content
        mock_response.info.return_value = {"Content-Encoding": "gzip"}
        mock_response.geturl.return_value = "http://example.com/index.m3u8"
        mock_response.headers = MockHeaders("utf-8")
        mock_open.return_value = mock_response

        content, base_uri = client.download("http://example.com/index.m3u8")

        self.assertEqual(content, original_content)
        self.assertEqual(base_uri, "http://example.com/")

    @patch("urllib.request.OpenerDirector.open")
    def test_download_with_proxy(self, mock_open):
        client = DefaultHTTPClient(proxies={"http": "http://proxy.example.com"})
        mock_response = Mock(spec=HTTPResponse)
        mock_response.read.return_value = b"playlist proxied content"
        mock_response.info.return_value = {}
        mock_response.geturl.return_value = "http://example.com/index.m3u8"
        mock_response.headers = MockHeaders()
        mock_open.return_value = mock_response

        content, base_uri = client.download("http://example.com/index.m3u8")

        self.assertEqual(content, "playlist proxied content")
        self.assertEqual(base_uri, "http://example.com/")


def _response(body, encoding=None):
    response = Mock(spec=HTTPResponse)
    response.read.return_value = body
    response.info.return_value = {"Content-Encoding": encoding} if encoding else {}
    response.geturl.return_value = "http://example.com/index.m3u8"
    response.headers = MockHeaders()
    return response


class TestDefaultHTTPClientDetails(unittest.TestCase):
    @patch("urllib.request.OpenerDirector.open")
    def test_response_is_closed(self, mock_open):
        response = _response(b"playlist")
        mock_open.return_value = response

        DefaultHTTPClient().download("http://example.com/index.m3u8")

        response.close.assert_called_once_with()

    @patch("urllib.request.OpenerDirector.open")
    def test_response_is_closed_when_it_cannot_be_decoded(self, mock_open):
        response = _response(b"not gzip", encoding="gzip")
        mock_open.return_value = response

        with self.assertRaises(OSError):
            DefaultHTTPClient().download("http://example.com/index.m3u8")

        response.close.assert_called_once_with()

    @patch("urllib.request.OpenerDirector.open")
    def test_content_encodings(self, mock_open):
        body = b"playlist"
        raw_deflate = zlib.compressobj(wbits=-zlib.MAX_WBITS)
        examples = {
            "GZIP": gzip.compress(body),
            "x-gzip": gzip.compress(body),
            " gzip ": gzip.compress(body),
            "deflate": zlib.compress(body),
            "Deflate": raw_deflate.compress(body) + raw_deflate.flush(),
            "identity": body,
        }

        for encoding, data in examples.items():
            with self.subTest(encoding=encoding):
                mock_open.return_value = _response(data, encoding)

                content, _ = DefaultHTTPClient().download("http://example.com/a.m3u8")

                self.assertEqual(content, "playlist")

    @patch("urllib.request.build_opener")
    def test_cookies_are_kept_between_downloads(self, mock_build_opener):
        jar = CookieJar()
        client = DefaultHTTPClient(cookie_jar=jar)
        mock_build_opener.return_value.open.return_value = _response(b"playlist")

        client.download("http://example.com/index.m3u8")
        client.download("http://example.com/index.m3u8")

        for call in mock_build_opener.call_args_list:
            cookie_handlers = [
                handler
                for handler in call.args
                if isinstance(handler, urllib.request.HTTPCookieProcessor)
            ]
            self.assertEqual(len(cookie_handlers), 1)
            self.assertIs(cookie_handlers[0].cookiejar, jar)

    def test_each_client_has_its_own_cookie_jar_by_default(self):
        self.assertIsNot(DefaultHTTPClient().cookie_jar, DefaultHTTPClient().cookie_jar)

    @patch("urllib.request.OpenerDirector.open")
    def test_headers_are_optional(self, mock_open):
        mock_open.return_value = _response(b"playlist")

        content, _ = DefaultHTTPClient().download(
            "http://example.com/index.m3u8", headers=None
        )

        self.assertEqual(content, "playlist")
