import hashlib

import numpy as np
import pytest
import torch
import torch.nn.functional as F

from terrafm_temporal.encoders.terrafm_wrapper import EMBED_DIM, N_TOKENS, TerraFMEncoder
from terrafm_temporal.encoders.third_party.terrafm import normalize, terrafm_base
from terrafm_temporal.utils import REPO_ROOT, repo_path

TP = REPO_ROOT / "src/terrafm_temporal/encoders/third_party"


@pytest.fixture(scope="module")
def enc():
    torch.manual_seed(0)
    return TerraFMEncoder(terrafm_base())


def _dn(b=1, seed=0):  # DN sintéticos, como o uint16 do BDC
    g = torch.Generator().manual_seed(seed)
    return torch.randint(0, 10000, (b, 12, 224, 224), generator=g).float()


@pytest.mark.parametrize("name,sha", [
    ("terrafm.py", "7cb9d66704e274064029c87d2519427c681cbb57bcf2f7b7966e60d4343cc3d1"),
    ("LICENSE", "51a131c1984492133be4e46532827427c3f46045f8114c3d3d9e06498ff71607")])
def test_vendored_files_match_upstream(name, sha):  # core.autocrlf=true: compara com LF
    assert hashlib.sha256((TP / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == sha


def test_forward_shape_dtype(enc):
    y = enc(_dn(2))
    assert y.shape == (2, N_TOKENS, EMBED_DIM) and y.dtype == torch.float32 and torch.isfinite(y).all()


def test_matches_upstream_l2a_path(enc):
    x = _dn()
    ref = enc.backbone.get_intermediate_layers(normalize(x, "s2_l2a"), n=1, is_l2a=True, norm=True)[0]
    assert torch.allclose(enc(x), ref, atol=1e-6)


def test_uses_l2a_stem_only(enc):
    calls = {"l2a": 0, "l1c": 0}
    pe = enc.backbone.patch_embed
    hooks = [pe.conv2d_s2_l2a.register_forward_hook(lambda *a: calls.update(l2a=calls["l2a"] + 1)),
             pe.conv2d_s2_l1c.register_forward_hook(lambda *a: calls.update(l1c=calls["l1c"] + 1))]
    try:
        enc(_dn())
    finally:
        for h in hooks: h.remove()
    assert calls == {"l2a": 1, "l1c": 0}


def test_uint16_input_matches_float32(enc):
    x = _dn()
    assert torch.allclose(enc(torch.from_numpy(x.numpy().astype(np.uint16))), enc(x), atol=1e-6)


def test_rejects_reflectance_scaled_input(enc):
    with pytest.raises(ValueError):
        enc(_dn() * 1e-4)


def test_accepts_nodata_tile(enc):  # nodata do BDC = 0; a validade do token é da F2
    assert torch.isfinite(enc(torch.zeros(1, 12, 224, 224, dtype=torch.uint16))).all()


@pytest.mark.parametrize("shape", [(1, 13, 224, 224), (1, 2, 224, 224), (1, 12, 256, 256), (12, 224, 224)])
def test_rejects_bad_shape(enc, shape):
    with pytest.raises(ValueError):
        enc(torch.full(shape, 1000.0))


def test_frozen_and_stays_eval(enc):
    enc.train()
    assert not enc.backbone.training
    assert not any(p.requires_grad for p in enc.parameters())
    assert not enc(_dn()).requires_grad


@pytest.mark.weights
def test_from_config_loads_checkpoint(real_encoder, terrafm_cfg):
    sd = torch.load(repo_path(terrafm_cfg["weights"]["path"]), map_location="cpu", weights_only=True)
    assert all(torch.equal(v, sd[k]) for k, v in real_encoder.backbone.state_dict().items())
    assert real_encoder.norm_tokens is True


@pytest.mark.gpu
@pytest.mark.weights
def test_fp16_autocast_matches_fp32(real_encoder):
    real_encoder.to("cuda")
    try:
        x = _dn(2).cuda()
        ref = real_encoder(x)
        with torch.autocast("cuda", dtype=torch.float16):
            y = real_encoder(x)
        assert torch.isfinite(y).all()
        assert F.cosine_similarity(y.float(), ref, dim=-1).mean() >= 0.99
    finally:
        real_encoder.to("cpu")
