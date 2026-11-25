"""Encoder TerraFM-B congelado: tensor de DN do Sentinel-2 L2A -> tokens de patch (PLANO §4.1)."""
from __future__ import annotations

from pathlib import Path

import torch
from torch import Tensor, nn

from terrafm_temporal.encoders.third_party.terrafm import TerraFM, normalize, terrafm_base
from terrafm_temporal.utils import repo_path

IMG_SIZE = 224
N_TOKENS = (IMG_SIZE // 16) ** 2  # 196 tokens de patch 16x16
EMBED_DIM = 768
N_BANDS = 12


def load_backbone(weights_path: Path) -> TerraFM:
    """TerraFM-B com os pesos oficiais. ``strict=True``: chaves divergentes são erro, não adaptação."""
    model = terrafm_base()
    state = torch.load(weights_path, map_location="cpu", weights_only=True)
    model.load_state_dict(state, strict=True)
    return model


class TerraFMEncoder(nn.Module):
    """Backbone congelado. Entrada ``[B,12,224,224]`` em DN (refletância x 10000); saída ``[B,196,768]``."""

    def __init__(self, backbone: TerraFM, norm_tokens: bool = True):
        super().__init__()
        self.backbone = backbone
        self.norm_tokens = norm_tokens
        self.requires_grad_(False)
        self.eval()

    @classmethod
    def from_config(cls, cfg: dict) -> "TerraFMEncoder":
        backbone = load_backbone(repo_path(cfg["weights"]["path"]))
        return cls(backbone, norm_tokens=cfg["norm_tokens"])

    def train(self, mode: bool = True) -> "TerraFMEncoder":
        super().train(mode)
        self.backbone.eval()  # congelado: sem dropout nem drop-path, mesmo em train()
        return self

    def forward(self, x: Tensor) -> Tensor:
        if x.ndim != 4 or x.shape[1] != N_BANDS or tuple(x.shape[-2:]) != (IMG_SIZE, IMG_SIZE):
            raise ValueError(
                f"expected input [B,{N_BANDS},{IMG_SIZE},{IMG_SIZE}], got {tuple(x.shape)}")
        if x.is_floating_point() and 0 < x.max() <= 1.0:
            raise ValueError(
                "TerraFM expects raw digital numbers (reflectance x 10000), "
                "but the input looks like reflectance in [0, 1]")
        # O cast vem antes de normalize(), que cria as estatísticas no dtype da entrada.
        x = x.to(torch.float32)
        with torch.no_grad():
            x = normalize(x, "s2_l2a")
            return self.backbone.get_intermediate_layers(
                x, n=1, is_l2a=True, norm=self.norm_tokens)[0]
