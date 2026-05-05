$files = Get-ChildItem -Path "$PSScriptRoot" -Recurse -Filter '*.yaml'
foreach ($f in $files) {
  if ($f.Name -eq '_convert_crlf.ps1') { continue }
  $content = [System.IO.File]::ReadAllText($f.FullName)
  $utf8NoBOM = New-Object System.Text.UTF8Encoding $false
  $lf = $content -replace "`r`n", "`n"
  [System.IO.File]::WriteAllText($f.FullName, $lf, $utf8NoBOM)
}
Write-Host 'Done converting all YAML files to LF UTF-8 no BOM'
