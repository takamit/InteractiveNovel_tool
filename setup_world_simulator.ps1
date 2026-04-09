param(
    [string]$ProjectRoot = "C:\Users\田中 拓実\Desktop\対話式小説"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== 対話式小説プロジェクトの初期構成を作成します ==="
Write-Host "ProjectRoot: $ProjectRoot"
Write-Host ""
Write-Host "この配布物は、すでにディレクトリとファイルが揃った状態です。"
Write-Host "必要に応じて次を実行してください:"
Write-Host "  Set-Location $ProjectRoot"
Write-Host "  python -m venv .venv"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  pip install -r requirements.txt"
Write-Host ""
