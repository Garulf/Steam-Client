import pytest

from steam_client.vdf_file import load_binary_vdf, load_vdf


def test_load_vdf_parses_text_vdf(tmp_path):
    path = tmp_path / "test.vdf"
    path.write_text('"root"\n{\n\t"key"\t"value"\n}\n')
    assert load_vdf(path) == {"root": {"key": "value"}}


def test_load_vdf_raises_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_vdf(tmp_path / "missing.vdf")


def test_load_binary_vdf_raises_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_binary_vdf(tmp_path / "missing.vdf")
