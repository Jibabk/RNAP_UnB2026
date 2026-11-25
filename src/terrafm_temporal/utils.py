"""Utilitários de configuração e download verificado por hash."""
from __future__ import annotations

import hashlib
import os
import urllib.request
from pathlib import Path

import yaml

# Raiz do repositório: src/terrafm_temporal/utils.py -> parents[2].
REPO_ROOT = Path(__file__).resolve().parents[2]

_CHUNK = 1024 * 1024  # 1 MiB


def repo_path(p: str | Path) -> Path:
    """Caminho relativo vira relativo à raiz do repositório; absoluto fica inalterado."""
    p = Path(p)
    return p if p.is_absolute() else REPO_ROOT / p


def load_config(path: str | Path) -> dict:
    """Lê um YAML (caminho relativo à raiz do repositório) com ``yaml.safe_load``."""
    with open(repo_path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def sha256_file(path: Path) -> str:
    """SHA-256 em hexadecimal, lido em blocos de 1 MiB."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(_CHUNK):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest: Path, sha256: str) -> Path:
    """Baixa ``url`` para ``dest`` verificando o SHA-256; idempotente.

    Se ``dest`` já existe e o hash confere, não acessa a URL. Caso contrário,
    grava em ``dest.name + ".part"`` e só move para ``dest`` se o hash conferir.
    """
    dest = Path(dest)
    if dest.exists() and sha256_file(dest) == sha256:
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    h = hashlib.sha256()
    with urllib.request.urlopen(url) as resp, open(part, "wb") as f:
        while chunk := resp.read(_CHUNK):
            f.write(chunk)
            h.update(chunk)

    got = h.hexdigest()
    if got != sha256:
        part.unlink()
        raise ValueError(f"sha256 mismatch for {url}: expected {sha256}, got {got}")
    os.replace(part, dest)
    return dest
