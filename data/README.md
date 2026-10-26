# data/

| Path | Content | In Git? |
|---|---|---|
| `raw/` | Original downloads (Parquet, XLSX). Recreate with `python -m src.download_data` | no |
| `processed/patch_designs.csv` | One row per patch design: parameters, S11-derived targets, labels, split | yes |
| `processed/mendeley_clean.csv` | Mendeley rows with `design_id` and `plausible` flag (CC BY 4.0, attribution in LICENSE) | yes |
| `processed/preprocessing_log.json` | Exclusion, duplicate and artefact counts | yes |
| `splits/*.csv` | Locked split manifests, identical to Module 1 | yes |
| `external/module1_vit_embeddings/` | 384-d ViT embeddings exported by Module 1 + `provenance.json` (SHA-256) | yes |
| `data_dictionary.csv` | Variable definitions, types and units | yes |

See `docs/DATA_CARD.md` for target definitions and the plausibility rule.
