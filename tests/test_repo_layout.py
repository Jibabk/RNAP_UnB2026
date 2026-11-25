import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("path", ["data/x.tif", "outputs/runs/a/metrics.json", "w/TerraFM-B.pth", "t/tile.zarr/.zgroup"])
def test_ignored(path):
    assert subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT).returncode == 0


@pytest.mark.parametrize("path", ["src/terrafm_temporal/__init__.py", "src/terrafm_temporal/data/__init__.py",
                                  "configs/data.yaml", "environment.yml"])
def test_not_ignored(path):
    assert subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT).returncode == 1


def test_roteiro_moved_to_docs():
    for name in ["roteiro_projeto2.tex", "roteiro_projeto2.pdf", "roteiro_projeto2_completo.tex"]:
        assert (ROOT / "docs/roteiro" / name).exists() and not (ROOT / name).exists()
