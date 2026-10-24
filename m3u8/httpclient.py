import contextlib
import gzip
import ssl
import urllib.request
import zlib
from http.cookiejar import CookieJar
from urllib.parse import urljoin


def _decompress(data, encoding):
    encoding = encoding.strip().lower()
    if encoding in ("gzip", "x-gzip"):
        return gzip.decompress(data)
    if encoding == "deflate":
        try:
            return zlib.decompress(data)
        except zlib.error:
            # some servers send the raw deflate stream without the zlib header
            return zlib.decompress(data, -zlib.MAX_WBITS)
    return data


class DefaultHTTPClient:
    """
    Downloads playlists with urllib.

    `proxies` is a dictionary of the proxies to use, ex.: {"https": "http://proxy"}
    `cookie_jar` keeps the cookies between the downloads of this client, a new
    `http.cookiejar.CookieJar` is used when it is not given
    """

    def __init__(self, proxies=None, cookie_jar=None):
        self.proxies = proxies
        self.cookie_jar = CookieJar() if cookie_jar is None else cookie_jar

    def download(self, uri, timeout=None, headers=None, verify_ssl=True):
        proxy_handler = urllib.request.ProxyHandler(self.proxies)
        https_handler = HTTPSHandler(verify_ssl=verify_ssl)
        cookie_handler = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        opener = urllib.request.build_opener(
            proxy_handler, https_handler, cookie_handler
        )
        opener.addheaders = list((headers or {}).items())
        with contextlib.closing(opener.open(uri, timeout=timeout)) as resource:
            base_uri = urljoin(resource.geturl(), ".")
            data = _decompress(
                resource.read(), resource.info().get("Content-Encoding") or ""
            )
            content = data.decode(resource.headers.get_content_charset(failobj="utf-8"))
        return content, base_uri


class HTTPSHandler:
    def __new__(self, verify_ssl=True):
        context = ssl.create_default_context()
        if not verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return urllib.request.HTTPSHandler(context=context)
