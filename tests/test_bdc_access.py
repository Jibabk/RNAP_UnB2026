"""Acesso ao BDC (pendências 9.1 e 9.3) e recorte real -> tokens do TerraFM."""
import numpy as np
import pytest
import pystac
import rasterio
import torch
from pyproj import Transformer
from pystac_client import Client
from rasterio.windows import Window

from terrafm_temporal.encoders.third_party.terrafm import S2_BANDS
from terrafm_temporal.utils import load_config

PROBE_DATES = "{year}-07-01/{year}-08-31"  # estação seca, menos nuvem


def _mini_item() -> pystac.Item:
    """Item mais antigo do mini-AOI no tile configurado, dentro da janela PROBE_DATES."""
    mini = load_config("configs/aoi.yaml")["mini"]
    bdc = load_config("configs/data.yaml")["bdc"]
    lon, lat = mini["center_lon"], mini["center_lat"]
    search = Client.open(bdc["stac_url"]).search(
        collections=[bdc["collection"]],
        bbox=(lon - 0.001, lat - 0.001, lon + 0.001, lat + 0.001),
        datetime=PROBE_DATES.format(year=mini["year"]),
        method="GET",  # o STAC do BDC só anuncia GET; o padrão POST gera aviso
    )
    items = [it for it in search.items() if f"_{mini['bdc_tile']}_" in it.id]
    assert items, "no BDC item found for the mini-AOI"
    return min(items, key=lambda it: it.datetime)


def _read_window(href: str) -> np.ndarray:
    """Lê a janela 224x224 centrada no ponto do mini-AOI (sem reprojetar)."""
    mini = load_config("configs/aoi.yaml")["mini"]
    with rasterio.open(href) as src:
        tr = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        x, y = tr.transform(mini["center_lon"], mini["center_lat"])
        row, col = src.index(x, y)
        window = Window(col - 112, row - 112, 224, 224)
        assert (
            window.col_off >= 0
            and window.row_off >= 0
            and window.col_off + 224 <= src.width
            and window.row_off + 224 <= src.height
        ), "window does not fit inside the raster"
        arr = src.read(1, window=window)
    # Os COGs do BDC estão gravados como int16, embora o STAC declare uint16.
    # O DN fica em [0, 10000+], então o cast sem perda para uint16 vale se não há negativos.
    assert arr.min() >= 0, "negative DN: cannot cast to uint16"
    return arr.astype(np.uint16)


def test_band_order_matches_terrafm():  # pendência 9.3, sem rede
    assert load_config("configs/data.yaml")["bdc"]["bands"] == S2_BANDS


@pytest.mark.network
def test_collection_lists_expected_assets():
    bdc = load_config("configs/data.yaml")["bdc"]
    coll = Client.open(bdc["stac_url"]).get_collection(bdc["collection"])
    assert set(bdc["bands"] + bdc["aux"]) <= set(coll.to_dict()["item_assets"])


@pytest.mark.network
def test_cog_window_reads_without_token():  # pendência 9.1
    item = _mini_item()
    band = item.assets["B04"].extra_fields["eo:bands"][0]
    assert band["nodata"] == 0 and band["scale"] == 0.0001
    arr = _read_window(item.assets["B04"].href)
    assert arr.shape == (224, 224) and arr.dtype == np.uint16


@pytest.mark.network
@pytest.mark.weights
def test_real_window_gives_tokens(real_encoder):
    bands = load_config("configs/data.yaml")["bdc"]["bands"]
    item = _mini_item()
    x = np.stack([_read_window(item.assets[b].href) for b in bands])[None]
    y = real_encoder(torch.from_numpy(x))
    assert y.shape == (1, 196, 768) and torch.isfinite(y).all() and y.std() > 0
