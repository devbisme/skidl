import pytest

from skidl.utilities import is_url


def test_unix_paths_not_urls():
    """Test that Unix paths are not recognized as URLs."""
    assert not is_url("/tmp/this.txt")  # Unix absolute path
    assert not is_url("../the-other.txt")  # Unix relative path
    assert not is_url("path.txt")  # Unix relative path without directory

def test_windows_paths_not_urls():
    """Test that Windows paths are not recognized as URLs."""
    assert not is_url(r"c:\some dir with silly spaces\FileinHorribleCase.dat")  # Windows absolute path
    assert not is_url(r"..\the-other.txt")  # Windows relative path
    # Apparently can largely get away with using / for \ in windows
    assert not is_url("C:/some dir with silly spaces/some file")  # Windows absolute path with forward slashes

def test_http_https_are_url():
    """Test that HTTP and HTTPS URLs are recognized as URLs."""
    assert is_url("http://example.com/resource")  # HTTP URL
    assert is_url("https://example.com/resouce")  # HTTPS URL
