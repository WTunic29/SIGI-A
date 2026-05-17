# Este script llegó a sobrescribir requests desde plantillas viejas (carpeta Usuarios/ eliminada,
# respuestas "envueltas" de negocios ≠ API actual plana).
#
# La colección canónica vive en: QA/postman/collections/SIGI-A/**/*.request.yaml
# Guía actualizada: QA/postman/README.md
#
# Para normalizar BOM/CRLF sobre todo QA/postman, usar: QA/_fix_all_yaml.ps1

Write-Host "Obsoleto: no regenera Postman desde aquí para evitar pisar QA/postman/" -ForegroundColor Yellow
exit 1
