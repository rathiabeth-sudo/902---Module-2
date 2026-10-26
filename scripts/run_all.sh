#!/usr/bin/env bash
# Module 2 full pipeline (Linux/macOS). A few minutes on a laptop CPU.
set -euo pipefail
PY=${PY:-python}
$PY -m src.download_data
$PY -m src.preprocessing
$PY -m src.numerical_model
$PY -m src.fusion_optimization
$PY -m pytest -q | tee results/test_report.txt
$PY scripts/make_deliverables.py
echo "MODULE 2 PIPELINE COMPLETE"
