$utf8NoBOM = New-Object System.Text.UTF8Encoding $false

$files = @(
  'QA\postman\collections\SIGI-A\Auth\Register.request.yaml',
  'QA\postman\collections\SIGI-A\Auth\Solo-Negocio.request.yaml',
  'QA\postman\collections\SIGI-A\Auth\Verify-2FA.request.yaml',
  'QA\postman\environments\SIGI-A-Local.env.yaml',
  'QA\postman\environments\SIGI-A.environment.yaml'
)

foreach ($f in $files) {
  if (-not (Test-Path $f)) {
    Write-Host "SKIP (no existe): $f"
    continue
  }
  $bytes = [System.IO.File]::ReadAllBytes($f)
  if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    $content = [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
    $content = $content -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($f, $content, $utf8NoBOM)
    Write-Host "Fixed BOM+CRLF: $f"
  } else {
    $content = [System.IO.File]::ReadAllText($f)
    $content = $content -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($f, $content, $utf8NoBOM)
    Write-Host "Fixed CRLF: $f"
  }
}
Write-Host "Done"
