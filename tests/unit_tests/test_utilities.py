from skidl.utilities import is_url


def test_unix_paths_not_urls():
    assert not is_url("/tmp/this.txt")
    assert not is_url("../the-other.txt")
    assert not is_url("path.txt")


def test_windows_paths_not_urls():
    assert not is_url(r"c:\some dir with silly spaces\FileinHorribleCase.dat")
    assert not is_url(r"..\the-other.txt")
    # Apparently can largely get away with using / for \ in windows
    assert not is_url("C:/some dir with silly spaces/some file")


def test_http_https_are_url():
    assert is_url("http://example.com/resource")
    assert is_url("https://example.com/resouce")
