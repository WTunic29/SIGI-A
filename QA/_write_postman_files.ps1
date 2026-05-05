
# Script para reescribir los archivos Postman de SIGI-A
$base = "QA\postman\collections\SIGI-A"
$env_path = "QA\postman\environments\SIGI-A-Local.env.yaml"

# LOGIN 
$login = '$kind: http-request
name: Login Usuario
description: ''Inicia sesion con correo y contrasena. El backend envia un codigo 2FA al correo. Usar Verify 2FA para obtener el token JWT.''
method: POST
url: ''{{base_url}}/auth/login''
order: 2000
headers:
  - key: Content-Type
    value: application/json
body:
  type: json
  content: |-
    {
      "correo": "juan@example.com",
      "password": "password123"
    }
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status 200 - Login exitoso", () => pm.response.to.have.status(200));
      pm.test("Respuesta tiene campo message", () => pm.expect(pm.response.json()).to.have.property("message"));
      pm.test("Requiere 2FA", () => pm.expect(pm.response.json()).to.have.property("requieres_2fa", true));
      pm.test("Respuesta tiene campo correo", () => pm.expect(pm.response.json()).to.have.property("correo"));
      const body = pm.response.json();
      if (body.correo) {
        pm.environment.set("correo_2fa", body.correo);
      }'
[System.IO.File]::WriteAllText("$base\Usuarios\Login.request.yaml", $login, [System.Text.Encoding]::UTF8)
Write-Host "OK: Login.request.yaml"

# registro
$register = '$kind: http-request
name: Register Usuario
description: ''Registra un nuevo usuario en el sistema. Devuelve el usuario creado. El campo rol es opcional (default: cliente).''
method: POST
url: ''{{base_url}}/auth/register''
order: 1000
headers:
  - key: Content-Type
    value: application/json
body:
  type: json
  content: |-
    {
      "nombre": "Juan",
      "apellido": "Perez",
      "correo": "juan@example.com",
      "telefono": "3001234567",
      "password": "password123",
      "rol": "cliente"
    }
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status 201 - Usuario creado", () => pm.response.to.have.status(201));
      pm.test("Respuesta tiene campo message", () => pm.expect(pm.response.json()).to.have.property("message"));
      pm.test("Respuesta tiene campo usuario", () => pm.expect(pm.response.json()).to.have.property("usuario"));
      const usuario = pm.response.json().usuario;
      if (usuario) {
        pm.test("Usuario tiene id", () => pm.expect(usuario).to.have.property("id"));
        pm.test("Usuario tiene nombre", () => pm.expect(usuario).to.have.property("nombre"));
        pm.test("Usuario tiene apellido", () => pm.expect(usuario).to.have.property("apellido"));
        pm.test("Usuario tiene correo", () => pm.expect(usuario).to.have.property("correo"));
        pm.test("Usuario tiene rol", () => pm.expect(usuario).to.have.property("rol"));
        pm.environment.set("id_usuario", usuario.id);
      }'
[System.IO.File]::WriteAllText("$base\Usuarios\Register.request.yaml", $register, [System.Text.Encoding]::UTF8)
Write-Host "OK: Register.request.yaml"

# VERIFY 2FA
$verify2fa = '$kind: http-request
name: Verify 2FA
description: ''Verifica el codigo 2FA enviado al correo. Devuelve el token JWT (access_token) y los datos del usuario. Guarda el token en el environment automaticamente.''
method: POST
url: ''{{base_url}}/auth/verify-2fa''
order: 3000
headers:
  - key: Content-Type
    value: application/json
body:
  type: json
  content: |-
    {
      "correo": "{{correo_2fa}}",
      "codigo": "123456"
    }
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status 200 - 2FA validado", () => pm.response.to.have.status(200));
      pm.test("Respuesta tiene campo message", () => pm.expect(pm.response.json()).to.have.property("message"));
      pm.test("Respuesta tiene access_token", () => pm.expect(pm.response.json()).to.have.property("access_token"));
      pm.test("Token type es bearer", () => pm.expect(pm.response.json()).to.have.property("token_type", "bearer"));
      pm.test("Respuesta tiene campo usuario", () => pm.expect(pm.response.json()).to.have.property("usuario"));
      const body = pm.response.json();
      if (body.access_token) {
        pm.environment.set("token", body.access_token);
      }
      const usuario = body.usuario;
      if (usuario) {
        pm.test("Usuario tiene id", () => pm.expect(usuario).to.have.property("id"));
        pm.test("Usuario tiene nombre", () => pm.expect(usuario).to.have.property("nombre"));
        pm.test("Usuario tiene correo", () => pm.expect(usuario).to.have.property("correo"));
        pm.test("Usuario tiene rol", () => pm.expect(usuario).to.have.property("rol"));
        pm.environment.set("id_usuario", usuario.id);
      }'
[System.IO.File]::WriteAllText("$base\Usuarios\Verify-2FA.request.yaml", $verify2fa, [System.Text.Encoding]::UTF8)
Write-Host "OK: Verify-2FA.request.yaml"

# GET ME 
$getme = '$kind: http-request
name: Get Me
description: ''Obtiene el perfil del usuario autenticado. Requiere token JWT en el header Authorization.''
method: GET
url: ''{{base_url}}/auth/me''
order: 4000
headers:
  - key: Authorization
    value: ''Bearer {{token}}''
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status 200 - Perfil obtenido", () => pm.response.to.have.status(200));
      pm.test("Respuesta tiene campo id", () => pm.expect(pm.response.json()).to.have.property("id"));
      pm.test("Respuesta tiene campo nombre", () => pm.expect(pm.response.json()).to.have.property("nombre"));
      pm.test("Respuesta tiene campo apellido", () => pm.expect(pm.response.json()).to.have.property("apellido"));
      pm.test("Respuesta tiene campo correo", () => pm.expect(pm.response.json()).to.have.property("correo"));
      pm.test("Respuesta tiene campo rol", () => pm.expect(pm.response.json()).to.have.property("rol"));'
[System.IO.File]::WriteAllText("$base\Usuarios\Get-Me.request.yaml", $getme, [System.Text.Encoding]::UTF8)
Write-Host "OK: Get-Me.request.yaml"

# SOLO NEGOCIO
$solonegocio = '$kind: http-request
name: Solo Negocio
description: ''Ruta protegida solo para usuarios con rol negocio. Requiere token JWT con rol negocio.''
method: GET
url: ''{{base_url}}/auth/solo-negocio''
order: 5000
headers:
  - key: Authorization
    value: ''Bearer {{token}}''
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status 200 - Acceso permitido", () => pm.response.to.have.status(200));
      pm.test("Respuesta tiene campo message", () => pm.expect(pm.response.json()).to.have.property("message"));
      pm.test("Mensaje de bienvenida negocio", () => pm.expect(pm.response.json().message).to.eql("Bienvenido negocio"));
      pm.test("Respuesta tiene campo usuario", () => pm.expect(pm.response.json()).to.have.property("usuario"));'
[System.IO.File]::WriteAllText("$base\Usuarios\Solo-Negocio.request.yaml", $solonegocio, [System.Text.Encoding]::UTF8)
Write-Host "OK: Solo-Negocio.request.yaml"

# CREAR NEGOCIO
$crearNegocio = '$kind: http-request
name: Crear Negocio
description: ''Crea un nuevo negocio para el usuario autenticado con rol negocio. El propietario se toma del token JWT. Requiere autenticacion JWT con rol negocio.''
method: POST
url: ''{{base_url}}/negocios/''
order: 1000
headers:
  - key: Content-Type
    value: application/json
  - key: Authorization
    value: ''Bearer {{token}}''
body:
  type: json
  content: |-
    {
      "nombre": "Salon Bella",
      "descripcion": "Centro de estetica y belleza",
      "direccion": "Calle 123 # 45-67",
      "telefono": "3009876543",
      "correo": "salon@bella.com"
    }
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status 201 - Negocio creado", () => pm.response.to.have.status(201));
      pm.test("Respuesta tiene campo message", () => pm.expect(pm.response.json()).to.have.property("message"));
      pm.test("Respuesta tiene campo negocio", () => pm.expect(pm.response.json()).to.have.property("negocio"));
      const negocio = pm.response.json().negocio;
      if (negocio) {
        pm.test("Negocio tiene id", () => pm.expect(negocio).to.have.property("id"));
        pm.test("Negocio tiene nombre", () => pm.expect(negocio).to.have.property("nombre"));
        pm.test("Negocio tiene descripcion", () => pm.expect(negocio).to.have.property("descripcion"));
        pm.test("Negocio tiene direccion", () => pm.expect(negocio).to.have.property("direccion"));
        pm.test("Negocio tiene telefono", () => pm.expect(negocio).to.have.property("telefono"));
        pm.test("Negocio tiene correo", () => pm.expect(negocio).to.have.property("correo"));
        pm.environment.set("id_negocio", negocio.id);
      }'
[System.IO.File]::WriteAllText("$base\Negocios\Crear-Negocio.request.yaml", $crearNegocio, [System.Text.Encoding]::UTF8)
Write-Host "OK: Crear-Negocio.request.yaml"

# LISTAR NEGOCIOS 
$listarNegocios = '$kind: http-request
name: Listar Negocios
description: ''Obtiene la lista de todos los negocios registrados. No requiere autenticacion.''
method: GET
url: ''{{base_url}}/negocios/''
order: 2000
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status 200 - Lista obtenida", () => pm.response.to.have.status(200));
      pm.test("Respuesta es un array", () => pm.expect(pm.response.json()).to.be.an("array"));
      const negocios = pm.response.json();
      if (negocios.length > 0) {
        const n = negocios[0];
        pm.test("Negocio tiene id_negocio", () => pm.expect(n).to.have.property("id_negocio"));
        pm.test("Negocio tiene nombre_negocio", () => pm.expect(n).to.have.property("nombre_negocio"));
      }'
[System.IO.File]::WriteAllText("$base\Negocios\Listar-Negocios.request.yaml", $listarNegocios, [System.Text.Encoding]::UTF8)
Write-Host "OK: Listar-Negocios.request.yaml"

# ENVIRONMENT
$envContent = 'name: SIGI-A Local
values:
  - key: base_url
    value: ''http://localhost:8000''
    type: default
    enabled: true
  - key: token
    value: ''''
    type: secret
    enabled: true
  - key: correo_2fa
    value: ''''
    type: default
    enabled: true
  - key: id_usuario
    value: ''''
    type: default
    enabled: true
  - key: id_negocio
    value: ''''
    type: default
    enabled: true'
[System.IO.File]::WriteAllText($env_path, $envContent, [System.Text.Encoding]::UTF8)
Write-Host "OK: SIGI-A-Local.env.yaml"

Write-Host ""
Write-Host "Todos los archivos escritos correctamente."
