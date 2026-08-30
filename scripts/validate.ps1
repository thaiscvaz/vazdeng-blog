# Wrapper PowerShell para validate_post.py.
# Uso:
#   .\scripts\validate.ps1                                  # valida todos
#   .\scripts\validate.ps1 -Strict                          # warnings reprovam
#   .\scripts\validate.ps1 -File content/blog/.../index.md  # arquivo unico

param(
    [string]$File,
    [switch]$Strict,
    [int]$MinScore = 8
)

$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $repoRoot

# $args e variavel automatica do PowerShell — reatribuir quebra o splat e falha
# sob Set-StrictMode. Usar um nome proprio.
$target = if ($File) { $File } else { "content/blog" }
$pyArgs = @($target, "--min-score", $MinScore)
if ($Strict) { $pyArgs += "--strict" }

python scripts/validate_post.py @pyArgs
exit $LASTEXITCODE
