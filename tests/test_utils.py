import hashlib

import pytest

from terrafm_temporal.utils import (
    REPO_ROOT,
    download_file,
    load_config,
    repo_path,
    sha256_file,
)


def test_repo_path_relative_is_under_repo_root():
    assert repo_path("configs/data.yaml") == REPO_ROOT / "configs/data.yaml"
    assert (REPO_ROOT / "pyproject.toml").exists()


def test_repo_path_absolute_unchanged(tmp_path):
    assert repo_path(tmp_path) == tmp_path


def test_load_config_reads_yaml(tmp_path):
    p = tmp_path / "c.yaml"; p.write_text("a: 1\nb: [x, y]\n")
    assert load_config(p) == {"a": 1, "b": ["x", "y"]}


def _src(tmp_path):
    src = tmp_path / "src.bin"; src.write_bytes(b"terrafm" * 1000)
    return src, hashlib.sha256(src.read_bytes()).hexdigest()


def test_download_file_ok(tmp_path):
    src, sha = _src(tmp_path); dest = tmp_path / "out/w.pth"
    assert download_file(src.as_uri(), dest, sha) == dest
    assert dest.read_bytes() == src.read_bytes()
    assert not dest.with_name(dest.name + ".part").exists()


def test_download_file_bad_hash_raises_and_cleans(tmp_path):
    src, _ = _src(tmp_path); dest = tmp_path / "w.pth"
    with pytest.raises(ValueError, match="sha256"):
        download_file(src.as_uri(), dest, "0" * 64)
    assert not dest.exists() and not dest.with_name(dest.name + ".part").exists()


def test_download_file_skips_when_present(tmp_path):
    src, sha = _src(tmp_path); dest = tmp_path / "w.pth"; dest.write_bytes(src.read_bytes())
    assert download_file((tmp_path / "missing.bin").as_uri(), dest, sha) == dest  # não acessa a URL


def test_download_file_replaces_corrupt_dest(tmp_path):
    src, sha = _src(tmp_path); dest = tmp_path / "w.pth"; dest.write_bytes(b"truncated")
    download_file(src.as_uri(), dest, sha)
    assert sha256_file(dest) == sha
