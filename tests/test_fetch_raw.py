"""No-data checks for the private Release restore boundary."""

import hashlib

import pytest

from pipeline.fetch_raw import safe_name, verify


@pytest.mark.parametrize("name", ["../data.csv", "folder/data.csv", "folder\\data.csv", ""])
def test_release_asset_names_must_be_basename(name):
    with pytest.raises(ValueError):
        safe_name(name)


def test_release_asset_requires_matching_size_and_checksum(tmp_path):
    asset = tmp_path / "asset.zip"
    asset.write_bytes(b"verified source")
    digest = hashlib.sha256(b"verified source").hexdigest()
    verify(asset, 15, digest)
    with pytest.raises(ValueError, match="Size mismatch"):
        verify(asset, 14, digest)
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        verify(asset, 15, "0" * 64)
