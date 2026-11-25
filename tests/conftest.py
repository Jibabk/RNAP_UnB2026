"""Fixtures de sessão compartilhadas pelos testes."""
import pytest

from terrafm_temporal.utils import load_config, repo_path


@pytest.fixture(scope="session")
def terrafm_cfg() -> dict:
    return load_config("configs/model/terrafm.yaml")


@pytest.fixture(scope="session")
def real_encoder(terrafm_cfg):
    """Encoder com os pesos reais, em CPU. Pula se os pesos não foram baixados."""
    if not repo_path(terrafm_cfg["weights"]["path"]).exists():
        pytest.skip("weights missing: run scripts/00_download_weights.py")
    from terrafm_temporal.encoders.terrafm_wrapper import TerraFMEncoder

    return TerraFMEncoder.from_config(terrafm_cfg)
