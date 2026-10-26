# Module 2 full pipeline (Windows PowerShell). Run from the repository root:  powershell -File scripts\run_all.ps1
$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
foreach ($a in @(@("-m", "src.download_data"), @("-m", "src.preprocessing"), @("-m", "src.numerical_model"), @("-m", "src.fusion_optimization"))) {
    Write-Host ">>> $a"
    & $py @a
    if ($LASTEXITCODE -ne 0) { throw "failed: $a" }
}
& $py -m pytest -q | Tee-Object -FilePath results\test_report.txt
& $py scripts\make_deliverables.py
Write-Host "MODULE 2 PIPELINE COMPLETE"
