$utf8NoBOM = New-Object System.Text.UTF8Encoding $false

$files = @(
  'QA\postman\collections\SIGI-A\Usuarios\Register.request.yaml',
  'QA\postman\collections\SIGI-A\Usuarios\Solo-Negocio.request.yaml',
  'QA\postman\collections\SIGI-A\Usuarios\Verify-2FA.request.yaml',
  'QA\postman\environments\SIGI-A-Local.env.yaml'
)

foreach ($f in $files) {
  $bytes = [System.IO.File]::ReadAllBytes($f)
  if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
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
