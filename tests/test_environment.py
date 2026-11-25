import importlib
import sys
from pathlib import Path

import pytest
import torch

MODULES = ["osgeo.gdal", "rasterio", "rioxarray", "xarray", "zarr", "geopandas", "shapely", "pyproj",
           "pystac_client", "odc.stac", "numpy", "pandas", "sklearn", "ruptures", "tqdm", "yaml",
           "matplotlib", "tensorboard", "ee", "torch", "mambapy"]


def test_python_311():
    assert sys.version_info[:2] == (3, 11)


@pytest.mark.parametrize("name", MODULES)
def test_import(name):
    importlib.import_module(name)


def test_package_is_editable_install():
    import terrafm_temporal
    root = Path(__file__).resolve().parents[1]
    assert Path(terrafm_temporal.__file__).resolve() == root / "src/terrafm_temporal/__init__.py"


@pytest.mark.gpu
def test_torch_cuda():
    assert torch.__version__ == "2.14.1+cu126"
    assert torch.cuda.is_available()
    assert "sm_75" in torch.cuda.get_arch_list()  # GTX 1650 e RTX 2070 são Turing (sm_75)


@pytest.mark.gpu
def test_mambapy_forward_cuda():
    from mambapy.mamba import Mamba, MambaConfig
    m = Mamba(MambaConfig(d_model=128, n_layers=1)).cuda()
    y = m(torch.randn(2, 207, 128, device="cuda"))
    assert y.shape == (2, 207, 128) and torch.isfinite(y).all()
