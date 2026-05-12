$utf8NoBOM = New-Object System.Text.UTF8Encoding $false

$files = Get-ChildItem -Path "QA\postman" -Recurse -Filter "*.yaml"

foreach ($f in $files) {
  $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
  if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    $content = [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
    $content = $content -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($f.FullName, $content, $utf8NoBOM)
    Write-Host "Fixed BOM+CRLF: $($f.FullName)"
  } else {
    $content = [System.IO.File]::ReadAllText($f.FullName)
    $content = $content -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($f.FullName, $content, $utf8NoBOM)
    Write-Host "Fixed CRLF: $($f.FullName)"
  }
}
Write-Host "Done - all YAML files normalized to UTF-8 no BOM, LF line endings"
