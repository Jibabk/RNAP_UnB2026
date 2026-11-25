# TerraFM (código de terceiros)

Esta pasta guarda uma cópia **sem nenhuma alteração** de dois arquivos do TerraFM, para que o encoder rode sem depender de rede.

## Origem
- Repositório: <https://github.com/mbzuai-oryx/TerraFM>
- Commit: `e245c347ab1ef94e8d14b40dcd5f12d310b03f32` (13/11/2026)
- Arquivos: `terrafm.py` e `LICENSE`, baixados de `raw.githubusercontent.com` nesse commit.
- Integridade (sha256, com quebras de linha LF; o teste `test_vendored_files_match_upstream` confere):
  - `terrafm.py`: `7cb9d66704e274064029c87d2519427c681cbb57bcf2f7b7966e60d4343cc3d1`
  - `LICENSE`: `51a131c1984492133be4e46532827427c3f46045f8114c3d3d9e06498ff71607`

## Licenças
- Código e pesos do TerraFM: MIT (ver `LICENSE`).
- Trechos copiados e adaptados do DINO (<https://github.com/facebookresearch/dino>): Apache-2.0, como indica o cabeçalho de `terrafm.py`.

## Nota sobre o arquivo
`_no_grad_trunc_normal_` chama `warnings.warn` sem importar `warnings`. O ramo só roda na inicialização com média fora de [a, b], o que não acontece com os valores padrão; o arquivo foi mantido sem alterações.

## Uso no projeto
Não importe este módulo diretamente nos scripts: use `terrafm_temporal.encoders.terrafm_wrapper.TerraFMEncoder`, que fixa a entrada em DN, o stem L2A e a saída de tokens de patch.
