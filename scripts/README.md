# Scripts de Mantenimiento

Este directorio contiene scripts de PowerShell para el mantenimiento del proyecto SIGI-A.

## Scripts Disponibles

- `_fix_all_yaml.ps1` - Corrige problemas de formato en archivos YAML
- `_fix_bom.ps1` - Elimina BOM (Byte Order Mark) de archivos
- `_write_postman_files.ps1` - Genera archivos de configuración para Postman

## Uso

Ejecutar desde PowerShell en el directorio raíz del proyecto:

```powershell
.\scripts\_fix_all_yaml.ps1
.\scripts\_fix_bom.ps1
.\scripts\_write_postman_files.ps1
```
