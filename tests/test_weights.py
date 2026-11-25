import pytest

from terrafm_temporal.utils import load_config, repo_path, sha256_file


@pytest.mark.weights
def test_weights_file_matches_config():
    w = load_config("configs/model/terrafm.yaml")["weights"]
    p = repo_path(w["path"])
    if not p.exists():
        pytest.skip("weights missing: run scripts/00_download_weights.py")
    assert p.stat().st_size == w["size_bytes"] and sha256_file(p) == w["sha256"]
