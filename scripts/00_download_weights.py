"""Baixa os pesos do TerraFM-B conforme o YAML (URL e hash fixados) e verifica o SHA-256."""
from __future__ import annotations

import argparse

from terrafm_temporal.utils import download_file, load_config, repo_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True, help="YAML com a seção 'weights' (ex.: configs/model/terrafm.yaml)")
    args = ap.parse_args(argv)

    w = load_config(args.config)["weights"]
    dest = download_file(w["url"], repo_path(w["path"]), w["sha256"])
    print(f"OK {dest} sha256={w['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
