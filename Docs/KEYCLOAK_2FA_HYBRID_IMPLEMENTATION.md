# Guía Completa: Implementación de 2FA Híbrido con Keycloak

## Tabla de Contenidos
1. [Concepto Fundamental](#concepto-fundamental)
2. [Arquitectura Resultante](#arquitectura-resultante)
3. [Flujo Detallado de Autenticación](#flujo-detallado-de-autenticación)
4. [Gestión de Usuarios y Sincronización](#gestión-de-usuarios-y-sincronización)
5. [Cambios en Base de Datos](#cambios-en-base-de-datos)
6. [Configuración de Keycloak](#configuración-de-keycloak)
7. [Flujos Adicionales](#flujos-adicionales)
8. [Ventajas y Desventajas](#ventajas-y-desventajas)
9. [Consideraciones de Implementación](#consideraciones-de-implementación)
10. [Comparación con Alternativas](#comparación-con-alternativas)

---

## Concepto Fundamental

Esta opción mantiene **tu arquitectura actual intacta** (FastAPI + JWT + PostgreSQL) y usa Keycloak **únicamente** como un servicio especializado de validación de segundo factor. Es como agregar un "módulo de seguridad adicional" sin reestructurar todo el edificio.

**Propósito de Keycloak en este modelo:**
- Almacena y valida secretos OTP (One-Time Password)
- Expone API para verificar códigos 2FA
- Gestiona políticas de seguridad OTP
- Proporciona audit logs de intentos 2FA

**Lo que tu Gateway sigue haciendo:**
- Gestión completa de usuarios en PostgreSQL
- Primer factor: validación usuario/contraseña
- Segundo factor: llamada a Keycloak para validar OTP
- Emisión de JWT propio
- Proxy de requests protegidos al Flask API

---

## Arquitectura Resultante

### Separación de Responsabilidades

```
┌─────────────────────────────────────────┐
│         Cliente / Frontend              │
│    (navegador, app mobile, etc)         │
└────────────────────┬────────────────────┘
                     │
         ┌───────────┴────────────┐
         │                        │
         ▼                        ▼
┌──────────────────────┐  ┌──────────────────────┐
│  Tu FastAPI Gateway  │  │     Keycloak Server  │
│  (Responsable de):   │  │   (Responsable de):  │
│                      │  │                      │
│ • Primer factor      │  │ • Validar OTP       │
│ • JWT propio         │  │ • Almacenar secret  │
│ • Usuarios DB        │  │ • Policies OTP      │
│ • Proxy al Flask API │  │ • Audit logs        │
└────────┬─────────────┘  └──────────┬──────────┘
         │                           │
         └───────────────┬───────────┘
                         │
                         ▼
        ┌────────────────────────────┐
        │  PostgreSQL (Tu DB)        │
        │  • Users                   │
        │  • Roles/Permisos          │
        │  • 2FA Settings            │
        │  • 2FA Challenges          │
        └────────────────────────────┘
```

### División de Componentes

**Tu API Gateway (FastAPI):**
- Sigue gestionando usuarios en PostgreSQL
- Maneja primer factor (usuario/contraseña)
- Genera y valida tus propios JWT
- Proxea requests al Flask API
- Controla toda la lógica de negocio de autenticación

**Keycloak:**
- **SOLO** valida códigos OTP (One-Time Password)
- Actúa como servicio de verificación externa
- No conoce tus usuarios completos
- No emite tokens que uses en tu aplicación
- Es un "validador de segundo factor" aislado

---

## Flujo Detallado de Autenticación

### Fase 1: Primer Factor (Tu Sistema Actual)

#### 1. Request Inicial

```
POST /auth/login
{
  "username": "jugador123",
  "password": "miContraseña123!"
}
```

Tu endpoint recibe credenciales normalmente.

#### 2. Validación de Credenciales

El proceso es como funciona actualmente:

1. Busca usuario en PostgreSQL por username
2. Verifica contraseña usando bcrypt (si coincide)
3. Si falla validación: retorna error HTTP 401
4. Si pasa validación: **NO emites JWT todavía** (aquí está el cambio clave)

```python
# Pseudocódigo del cambio
if not valid_credentials:
    return error_401()

# Antes (tu flujo actual):
# jwt_token = generate_jwt(user)
# return {"access_token": jwt_token}

# Ahora (nuevo flujo):
# Continúa a Fase 2
```

#### 3. Decisión de Flujo

Tu gateway consulta si el usuario tiene 2FA:

```python
user = get_user_from_db(username)
if user.two_factor_enabled == False:
    # Flujo normal: emites JWT y listo
    jwt_token = generate_jwt(user)
    return {"access_token": jwt_token, "token_type": "Bearer"}
else:
    # 2FA habilitado: Inicia segundo factor
    initiate_2fa(user)
```

---

### Fase 2: Iniciación del Segundo Factor

#### 4. Generación de Token Temporal

Creas un **JWT temporal de corta duración** (máximo 10 minutos):

```python
# Token temporal que significa:
# "Este usuario pasó primer factor, espera OTP"

temp_token_claims = {
    "user_id": user.id,
    "status": "pending_2fa",
    "exp": datetime.utcnow() + timedelta(minutes=10),
    "challenge_id": str(uuid4())  # ID único de este desafío
}

temp_token = create_jwt(
    claims=temp_token_claims,
    secret=SECRET_2FA  # Secret diferente al JWT normal
)
```

Almacenas este estado en base de datos (tabla `2fa_challenges`):

```python
challenge = 2FAChallenge(
    id=temp_token_claims["challenge_id"],
    user_id=user.id,
    challenge_token_hash=hash_token(temp_token),
    created_at=datetime.utcnow(),
    expires_at=datetime.utcnow() + timedelta(minutes=10),
    attempts=0,  # Contador de intentos fallidos
    status="pending"
)
db.add(challenge)
db.commit()
```

#### 5. Respuesta al Cliente

```json
{
  "success": true,
  "message": "Primer factor válido. Se requiere código OTP",
  "data": {
    "requires_2fa": true,
    "temp_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "challenge_id": "550e8400-e29b-41d4-a716-446655440000",
    "otp_method": "totp"
  },
  "timestamp": "2025-11-04T10:30:00"
}
```

#### 6. Frontend Reacciona

Frontend ahora:

1. Guarda `temp_token` en memoria (NO localStorage por seguridad)
2. Guarda `challenge_id`
3. Muestra formulario de entrada para código OTP
4. Usuario abre su app Google Authenticator
5. Lee código de 6 dígitos (ej: 123456)
6. Ingresa código en el formulario

---

### Fase 3: Integración con Keycloak

#### Configuración Previa de Keycloak

**Opción A: Usuarios Independientes (Más Simple)**

Creas usuarios en Keycloak con username igual al de PostgreSQL:

```
PostgreSQL User:          Keycloak User:
- id: 123                - sub (subject): uuid-xxx
- username: jugador123   - username: jugador123
- email: jugador@...     - email: jugador@...
- two_factor_enabled     (OTP configurado)
```

Ventajas:
- Más fácil de implementar
- No requiere sincronización realtime
- Cada sistema maneja sus datos

Desventajas:
- Duplicación de datos
- Necesitas sincronización eventual

**Opción B: Federación de Usuario (Más Avanzado)**

Keycloak se federar con tu PostgreSQL:

- Keycloak consulta tu DB directamente
- No duplica datos de usuario
- Solo almacena OTP en Keycloak

Desventajas:
- Más complejo de configurar
- Requiere que tu DB sea accesible desde Keycloak

**Configuración OTP en Keycloak:**

En Keycloak Admin Console:

1. **Realm Settings → Authentication → TOTP Policy**
   - Type: Time-based (TOTP)
   - Algorithm: SHA-256
   - Number of Digits: 6
   - Time Period: 30 segundos

2. **Cada Usuario Configurado en Keycloak:**
   - Cuando se registra/habilita 2FA
   - Keycloak genera QR code (formato QR estándar)
   - Usuario escanea con Google Authenticator, Authy, Microsoft Authenticator
   - App genera códigos cada 30 segundos
   - Keycloak almacena secret encriptado

#### 7. Usuario Envía Código OTP

```
POST /auth/verify-2fa
{
  "temp_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "challenge_id": "550e8400-e29b-41d4-a716-446655440000",
  "otp_code": "123456"
}
```

#### 8. Tu Gateway Valida Contexto

Antes de llamar Keycloak, validas que tu sistema esté consistente:

```python
# 1. Verificar temp_token
try:
    temp_claims = verify_jwt(temp_token, secret=SECRET_2FA)
except ExpiredSignatureError:
    return error(message="Token expirado. Inicia sesión nuevamente")

# 2. Verificar challenge_id existe y es válido
challenge = db.query(2FAChallenge).filter(
    2FAChallenge.id == challenge_id
).first()

if not challenge:
    return error(message="Challenge no encontrado")

if challenge.status != "pending":
    return error(message="Challenge ya fue procesado")

if challenge.expires_at < datetime.utcnow():
    return error(message="Challenge expirado")

if challenge.attempts >= 5:
    return error(message="Demasiados intentos fallidos. Intenta de nuevo más tarde")

# 3. Extraer user_id
user_id = temp_claims["user_id"]
user = db.query(User).filter(User.id == user_id).first()

if not user:
    return error(message="Usuario no encontrado")

if not user.keycloak_user_id:
    return error(message="Usuario no tiene 2FA configurado en Keycloak")
```

#### 9. Comunicación con Keycloak

Aquí llamas la **API REST de Keycloak**.

**Obtener Service Account Token (paso previo):**

Tu gateway necesita autenticarse con Keycloak:

```python
# Al iniciar la aplicación, obtienes token de servicio:
response = httpx.post(
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
    data={
        "grant_type": "client_credentials",
        "client_id": "api-gateway-2fa-service",
        "client_secret": KEYCLOAK_CLIENT_SECRET
    }
)

service_account_token = response.json()["access_token"]
# Guardas este token y lo reutilizas (expira en minutos/horas)
```

**Validar OTP en Keycloak:**

Hay varias formas. La más directa es usar el endpoint de credenciales:

```python
# Llamada a Keycloak Admin API para verificar OTP
response = httpx.post(
    f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user.keycloak_user_id}/execute-actions-email",
    headers={
        "Authorization": f"Bearer {service_account_token}",
        "Content-Type": "application/json"
    },
    json={
        "actions": ["VERIFY_OTP"],
        "otp": otp_code
    }
)
```

**Respuesta de Keycloak:**

```
Código HTTP 204 No Content: OTP válido
Código HTTP 400 Bad Request: OTP inválido
Código HTTP 401 Unauthorized: Token de servicio expirado
Código HTTP 404 Not Found: Usuario o credencial OTP no existe
```

#### 10. Keycloak Responde

**Si OTP es Válido (200/204):**

```python
if response.status_code in [200, 204]:
    # OTP validó correctamente
    # Continúa a Fase 4
    pass
```

**Si OTP es Inválido (400):**

```python
elif response.status_code == 400:
    # Incrementar contador de intentos
    challenge.attempts += 1
    db.commit()
    
    if challenge.attempts >= 5:
        challenge.status = "failed"
        db.commit()
        return error(
            message="Demasiados intentos. Por favor intenta más tarde",
            status_code=429
        )
    else:
        remaining = 5 - challenge.attempts
        return error(
            message=f"OTP inválido. {remaining} intentos restantes",
            status_code=400
        )
```

---

### Fase 4: Emisión de JWT Final

#### 11. Si Keycloak Valida OTP Exitosamente

Generas tu JWT completo tradicional:

```python
if response.status_code in [200, 204]:
    # Marcar challenge como completado
    challenge.status = "verified"
    challenge.verified_at = datetime.utcnow()
    db.commit()
    
    # Generar JWT completo
    jwt_claims = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [r.name for r in user.roles],
        "two_factor_verified": True,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    
    access_token = create_jwt(
        claims=jwt_claims,
        secret=SECRET_JWT  # Secret diferente al de temp token
    )
    
    refresh_token = create_jwt(
        claims={"user_id": user.id, "type": "refresh"},
        secret=SECRET_REFRESH,
        expires_in=timedelta(days=7)
    )
```

#### 12. Respuesta Final al Cliente

```json
{
  "success": true,
  "message": "Autenticación completa",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": 123,
      "username": "jugador123",
      "email": "jugador@example.com",
      "roles": ["player", "verified"]
    }
  },
  "timestamp": "2025-11-04T10:32:45"
}
```

#### 13. Si Keycloak Rechaza OTP

Ya se maneja en sección anterior, pero resumen:

- Retornas error específico (401 Unauthorized)
- Permites reintentos (límite de 5)
- `temp_token` sigue válido para reintentar
- Bloqueas acceso tras múltiples fallos
- Cliente debe iniciar login desde cero tras X fallos

```json
{
  "success": false,
  "message": "OTP inválido. 3 intentos restantes",
  "data": null,
  "timestamp": "2025-11-04T10:32:50",
  "error_code": "INVALID_OTP"
}
```

---

## Gestión de Usuarios y Sincronización

### El Problema: Dos Sistemas de Usuarios

Como mantienes PostgreSQL **Y** usas Keycloak, tienes duplicación:

```
PostgreSQL              Keycloak
───────────              ────────
• jugador123           • jugador123 (username)
• email: ...           • email: ...
• password_hash        • OTP secret (encriptado)
• two_factor_enabled   • OTP status
• roles                • (no tiene roles de tu app)
• permisos             • (no tiene permisos de tu app)
```

**Necesitas estrategia de sincronización.**

### Registro de Nuevo Usuario

Cuando un usuario se registra:

```
POST /auth/register
{
  "username": "nuevo_jugador",
  "email": "nuevo@example.com",
  "password": "contraseña123!",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

#### Proceso:

1. **Validar datos**
   - Username único en tu DB
   - Email válido y único
   - Contraseña cumple requisitos

2. **Crear usuario en PostgreSQL**
   ```python
   user = User(
       username=data.username,
       email=data.email,
       password_hash=bcrypt_hash(data.password),
       first_name=data.first_name,
       last_name=data.last_name,
       two_factor_enabled=False,  # No habilitado por defecto
       keycloak_user_id=None
   )
   db.add(user)
   db.commit()
   ```

3. **Decidir si habilitar 2FA obligatorio**
   - Política A: 2FA opcional (usuario decide después)
   - Política B: 2FA obligatorio desde primer login
   
   ```python
   if REQUIRE_2FA_ON_SIGNUP:
       user.two_factor_enabled = True
       db.commit()
       return {
           "message": "Debes configurar 2FA para continuar",
           "setup_2fa_url": "/auth/setup-2fa"
       }
   else:
       return {
           "message": "Usuario registrado. Puedes habilitar 2FA en tu perfil",
           "login_url": "/auth/login"
       }
   ```

4. **Si 2FA habilitado, crear usuario en Keycloak**
   ```python
   # Solo si se requiere 2FA
   response = httpx.post(
       f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users",
       headers={"Authorization": f"Bearer {service_token}"},
       json={
           "username": data.username,
           "email": data.email,
           "firstName": data.first_name,
           "lastName": data.last_name,
           "enabled": True
       }
   )
   
   keycloak_user_id = response.headers.get("Location").split("/")[-1]
   
   # Guardar referencia en tu DB
   user.keycloak_user_id = keycloak_user_id
   db.commit()
   ```

5. **Si Keycloak creado exitosamente, enviar QR**
   ```python
   # Solicitar a Keycloak que genere credencial OTP
   otp_response = httpx.post(
       f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users/{keycloak_user_id}/credentials",
       headers={"Authorization": f"Bearer {service_token}"},
       json={
           "type": "otp",
           "algorithm": "HmacSHA256",
           "digits": 6,
           "period": 30
       }
   )
   
   qr_code_url = otp_response.json().get("qrCode")
   
   # Retornar QR al usuario
   return {
       "message": "Escanea el código QR con tu app de autenticación",
       "qr_code": qr_code_url,
       "manual_entry_key": otp_response.json().get("key")
   }
   ```

### Habilitación de 2FA en Usuario Existente

Usuario autenticado solicita habilitar 2FA:

```
POST /auth/enable-2fa
Headers: Authorization: Bearer {access_token}
```

#### Proceso:

1. **Verificar usuario autenticado**
   ```python
   current_user = verify_jwt(access_token)
   user = get_user(current_user["user_id"])
   ```

2. **Verificar que aún no tiene 2FA**
   ```python
   if user.two_factor_enabled:
       return error(message="Ya tiene 2FA habilitado")
   ```

3. **Crear usuario en Keycloak si no existe**
   ```python
   if not user.keycloak_user_id:
       # Crear en Keycloak
       response = httpx.post(...)
       user.keycloak_user_id = response.json()["id"]
       db.commit()
   ```

4. **Generar y retornar QR**
   ```python
   otp_response = httpx.post(
       f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user.keycloak_user_id}/credentials",
       ...
   )
   
   return {
       "qr_code": otp_response.json().get("qrCode"),
       "backup_codes": generate_backup_codes(user.id)  # Opcional
   }
   ```

5. **Requerir confirmación**
   
   El usuario debe escanear QR y proporcionar un código válido:
   
   ```
   POST /auth/confirm-2fa
   {
     "otp_code": "123456"
   }
   ```
   
   ```python
   # Verificar código con Keycloak
   response = httpx.post(
       f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user.keycloak_user_id}/verify-otp",
       json={"otp": otp_code}
   )
   
   if response.status_code == 200:
       user.two_factor_enabled = True
       user.two_factor_method = "totp"
       user.two_factor_configured_at = datetime.utcnow()
       db.commit()
       return {"message": "2FA habilitado exitosamente"}
   ```

### Deshabilitación de 2FA

Usuario autenticado solicita deshabilitar 2FA:

```
DELETE /auth/disable-2fa
Headers: Authorization: Bearer {access_token}
Body: {
  "password": "mi_contraseña",
  "otp_code": "123456"
}
```

#### Proceso:

1. **Verificar credenciales para seguridad**
   ```python
   current_user = verify_jwt(access_token)
   user = get_user(current_user["user_id"])
   
   # Requiere contraseña actual + OTP
   if not verify_password(password, user.password_hash):
       return error(message="Contraseña incorrecta")
   
   if not verify_otp_with_keycloak(user.keycloak_user_id, otp_code):
       return error(message="OTP incorrecto")
   ```

2. **Eliminar credencial OTP en Keycloak**
   ```python
   response = httpx.delete(
       f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user.keycloak_user_id}/credentials/otp",
       headers={"Authorization": f"Bearer {service_token}"}
   )
   ```

3. **Actualizar en PostgreSQL**
   ```python
   user.two_factor_enabled = False
   user.two_factor_method = None
   db.commit()
   
   return {"message": "2FA deshabilitado"}
   ```

### Eliminación de Usuario

Cuando usuario solicita eliminar cuenta:

```
DELETE /auth/delete-account
Headers: Authorization: Bearer {access_token}
```

#### Proceso:

1. **Verificar en Keycloak y eliminar OTP**
   ```python
   if user.keycloak_user_id:
       # Eliminar usuario de Keycloak
       httpx.delete(
           f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user.keycloak_user_id}",
           headers={"Authorization": f"Bearer {service_token}"}
       )
   ```

2. **Eliminar de PostgreSQL**
   ```python
   # Eliminar en cascada: tokens, challenges, etc.
   db.delete(user)
   db.commit()
   ```

3. **Cleanup**
   ```python
   # Limpiar desafíos 2FA del usuario
   db.query(2FAChallenge).filter(
       2FAChallenge.user_id == user.id
   ).delete()
   db.commit()
   ```

---

## Cambios en Base de Datos

### Tabla `users` Modificada

Necesitas agregar campos a tu tabla existente:

```sql
ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN two_factor_method VARCHAR(50);  -- 'totp', 'sms', 'email'
ALTER TABLE users ADD COLUMN keycloak_user_id VARCHAR(36);   -- UUID de Keycloak
ALTER TABLE users ADD COLUMN two_factor_configured_at TIMESTAMP;
ALTER TABLE users ADD COLUMN two_factor_backup_codes JSON;   -- Array de códigos
```

**Descripción de campos:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `two_factor_enabled` | BOOLEAN | Si 2FA está activo para este usuario |
| `two_factor_method` | VARCHAR | Tipo: 'totp' (Google Authenticator), 'sms', 'email', 'webauthn' |
| `keycloak_user_id` | VARCHAR | UUID que Keycloak asigna al usuario |
| `two_factor_configured_at` | TIMESTAMP | Cuándo se configuró 2FA |
| `two_factor_backup_codes` | JSON | Array de códigos de respaldo (hasheados) |

### Nueva Tabla: `2fa_challenges`

Para gestionar tokens temporales de segundo factor:

```sql
CREATE TABLE 2fa_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    challenge_token_hash VARCHAR(255) NOT NULL,  -- Hash del JWT temporal
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    attempts INTEGER DEFAULT 0,  -- Contador de intentos fallidos
    status VARCHAR(50) DEFAULT 'pending',  -- pending, verified, failed, expired
    verified_at TIMESTAMP,
    failed_at TIMESTAMP,
    ip_address VARCHAR(45),  -- Para auditoría
    user_agent TEXT,  -- Para auditoría
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_2fa_challenges_user ON 2fa_challenges(user_id);
CREATE INDEX idx_2fa_challenges_expires ON 2fa_challenges(expires_at);
CREATE INDEX idx_2fa_challenges_status ON 2fa_challenges(status);
```

**Descripción de campos:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único del desafío |
| `user_id` | INTEGER | Referencia al usuario |
| `challenge_token_hash` | VARCHAR | Hash del JWT temporal (no guardes en texto plano) |
| `created_at` | TIMESTAMP | Cuándo se creó el desafío |
| `expires_at` | TIMESTAMP | Cuándo expira (máximo 10 minutos después) |
| `attempts` | INTEGER | Número de intentos de OTP fallidos |
| `status` | VARCHAR | Estado: pending (esperando OTP), verified (completado), failed (múltiples fallos), expired (tiempo agotado) |
| `verified_at` | TIMESTAMP | Cuándo se verificó exitosamente |
| `failed_at` | TIMESTAMP | Cuándo se marcó como fallido |
| `ip_address` | VARCHAR | IP del cliente (auditoría) |
| `user_agent` | TEXT | User agent del navegador (auditoría) |

### Nueva Tabla: `2fa_audit_logs` (Opcional pero Recomendado)

Para auditoría detallada:

```sql
CREATE TABLE 2fa_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- setup, verify, fail, disable, reset
    event_status VARCHAR(50) NOT NULL,  -- success, failure
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSON,  -- Detalles adicionales
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_2fa_audit_logs_user ON 2fa_audit_logs(user_id);
CREATE INDEX idx_2fa_audit_logs_event ON 2fa_audit_logs(event_type);
```

---

## Configuración de Keycloak

### Instalación y Despliegue

**Opción 1: Docker Local (Desarrollo)**

```yaml
version: '3.8'

services:
  keycloak-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: keycloak_password
    volumes:
      - keycloak_db_data:/var/lib/postgresql/data

  keycloak:
    image: quay.io/keycloak/keycloak:24.0
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://keycloak-db:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: keycloak_password
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin123
    ports:
      - "8080:8080"
    command: start-dev
    depends_on:
      - keycloak-db

volumes:
  keycloak_db_data:
```

**Opción 2: Railway (Producción)**

- Crear PostgreSQL en Railway
- Crear Keycloak como servicio (imagen Docker)
- Variables de entorno para DB
- Configurar dominio personalizado

### Configuración del Realm

#### 1. Crear Realm

En Keycloak Admin Console:

1. Click en "Create Realm"
2. Nombre: `videogames-api-2fa`
3. Enabled: ON
4. Save

#### 2. Configurar Client

1. Left menu → Clients
2. Click "Create client"
3. **Client ID**: `api-gateway-2fa-service`
4. **Name**: API Gateway 2FA Service
5. Click Next
6. En "Capability config":
   - **Client authentication**: ON
   - **Authorization**: OFF
   - **Authentication flow**: Service Account Flows (check)
7. Click Save
8. En tab "Credentials":
   - Copy **Client Secret** (guardar en `.env`)
9. En tab "Service Account Roles":
   - Click "Assign a role"
   - Search: `manage-users`
   - Assign

#### 3. Configurar OTP Policy

1. Left menu → Authentication → Policies
2. OTP Policy:
   - **Type**: Time-based (TOTP)
   - **Algorithm**: SHA256
   - **Number of Digits**: 6
   - **Look ahead window**: 1
   - **Look back window**: 0
   - **Initial Counter**: 0
3. Save

#### 4. Habilitar OTP en Authentication Flow

1. Left menu → Authentication → Flows
2. Seleccionar "Direct Grant Flow"
3. Agregar ejecución: OTP Form (opcional si quieres 2FA en todos los logins)
4. Para este proyecto, dejas OTP como optional, ya que lo manejas en tu gateway

### Crear Usuario de Prueba

1. Left menu → Users
2. Click "Create new user"
3. Username: `testuser`
4. Email: `test@example.com`
5. First Name: Test
6. Last Name: User
7. Enabled: ON
8. Save

**Configurar OTP manual:**

1. Tab "Credentials"
2. Click "Set password"
3. Ingresa contraseña temporal
4. Save
5. Tab "Credentials" → Click "Set OTP"
6. Genera QR

### Variables de Entorno

Agregar a tu [`.env`](.env):

```dotenv
# Keycloak Configuration
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=videogames-api-2fa
KEYCLOAK_CLIENT_ID=api-gateway-2fa-service
KEYCLOAK_CLIENT_SECRET=your-super-secret-client-secret-here

# 2FA Configuration
TWO_FACTOR_SECRET_KEY=your-jwt-secret-for-2fa-tokens
TWO_FACTOR_TOKEN_EXPIRY_MINUTES=10
TWO_FACTOR_MAX_ATTEMPTS=5

# Existing
DATABASE_URL=postgresql+asyncpg://user:password@localhost/api_auth
FLASK_API_URL=https://flaskapi-production-a966.up.railway.app
SECRET_KEY=your-main-jwt-secret
```

---

## Flujos Adicionales

### Recuperación de Acceso (Usuario Pierde Dispositivo)

Escenario: Usuario pierde su teléfono con Google Authenticator configurado.

#### Opción A: Códigos de Respaldo

Al configurar 2FA, generas códigos backup:

```python
def generate_backup_codes(count=10):
    """Genera códigos de un solo uso para recuperación"""
    codes = []
    for _ in range(count):
        code = ''.join(secrets.choice('0123456789') for _ in range(8))
        codes.append(code)
    return codes
```

**Cuando usuario habilita 2FA:**

1. Generas 10 códigos
2. Los hashas (igual que contraseña)
3. Guardas hasheados en PostgreSQL: `two_factor_backup_codes`
4. Mostras al usuario (sin hashar) una sola vez
5. Usuario los guarda en lugar seguro

**Cuando usuario pierde dispositivo:**

1. En pantalla de login, usuario hace click "No puedo acceder a mi app"
2. Opción 1: Ingresa código backup en lugar de OTP
3. Tu gateway valida contra códigos guardados
4. Si coincide, marca como usado
5. Permite acceso

```python
@router.post("/auth/verify-2fa-backup")
async def verify_2fa_backup(data: VerifyBackupCodeRequest):
    challenge = db.query(2FAChallenge).filter(
        2FAChallenge.id == data.challenge_id
    ).first()
    
    user = challenge.user
    
    # Validar código backup
    for code_hash in user.two_factor_backup_codes or []:
        if bcrypt.verify(data.backup_code, code_hash):
            # Válido, marcar como usado
            user.two_factor_backup_codes.remove(code_hash)
            db.commit()
            
            # Generar JWT
            return jwt_response(user)
    
    return error(message="Código de respaldo inválido")
```

#### Opción B: Reset por Email

```python
@router.post("/auth/reset-2fa")
async def reset_2fa(data: ResetTwoFactorRequest):
    """Solicita reset de 2FA"""
    
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        return error(message="Usuario no encontrado")
    
    # Generar token de reset
    reset_token = create_jwt(
        claims={"user_id": user.id, "type": "2fa_reset"},
        secret=SECRET_2FA,
        expires_in=timedelta(hours=1)
    )
    
    # Enviar email
    send_email(
        to=user.email,
        subject="Reset de autenticación de dos factores",
        body=f"Click aquí para resetear: {FRONTEND_URL}/reset-2fa?token={reset_token}"
    )
    
    return {"message": "Email de reset enviado"}
```

El usuario hace click en link del email:

```python
@router.post("/auth/confirm-reset-2fa")
async def confirm_reset_2fa(data: ConfirmResetRequest):
    """Confirma reset requiriendo contraseña"""
    
    reset_claims = verify_jwt(data.reset_token, secret=SECRET_2FA)
    user = db.query(User).filter(User.id == reset_claims["user_id"]).first()
    
    # Requiere contraseña para seguridad
    if not verify_password(data.password, user.password_hash):
        return error(message="Contraseña incorrecta")
    
    # Eliminar OTP de Keycloak
    httpx.delete(
        f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user.keycloak_user_id}/credentials/otp",
        headers={"Authorization": f"Bearer {service_token}"}
    )
    
    # Deshabilitar en BD
    user.two_factor_enabled = False
    db.commit()
    
    # Retornar URL para reconfigurar si desea
    return {
        "message": "2FA reseteado. Puedes reconfigurarlo desde tu perfil"
    }
```

### Renovación de Token (Refresh)

Tu endpoint `/auth/refresh` existente:

**Cambio importante:**

```python
@router.post("/auth/refresh")
async def refresh_token(data: RefreshTokenRequest):
    """Refresca JWT sin requerir segundo factor"""
    
    # Si usuario tiene 2FA, NO requieres OTP nuevamente
    # El JWT original ya fue validado con 2FA completo
    
    try:
        claims = verify_jwt(data.refresh_token, secret=SECRET_REFRESH)
    except ExpiredSignatureError:
        return error(message="Refresh token expirado", status_code=401)
    
    user = db.query(User).filter(User.id == claims["user_id"]).first()
    
    # Generar nuevo JWT completo
    new_jwt = create_jwt(
        claims={
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [r.name for r in user.roles],
            "two_factor_verified": user.two_factor_enabled
        },
        secret=SECRET_JWT,
        expires_in=timedelta(hours=1)
    )
    
    return {
        "access_token": new_jwt,
        "token_type": "Bearer",
        "expires_in": 3600
    }
```

**Por qué no requiere 2FA:**

El JWT original contiene claim `two_factor_verified: True` (si lo habilitó). Al refrescar, confías en que el JWT anterior fue validado correctamente.

### Cambio de Contraseña

Cuando usuario cambia contraseña:

```python
@router.post("/auth/change-password")
async def change_password(data: ChangePasswordRequest):
    """Cambia contraseña con verificación de seguridad"""
    
    current_user = verify_jwt(access_token)
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    # 1. Verificar contraseña actual
    if not verify_password(data.current_password, user.password_hash):
        return error(message="Contraseña actual incorrecta")
    
    # 2. Si tiene 2FA, también requiere OTP
    if user.two_factor_enabled:
        # Validar OTP con Keycloak
        otp_response = httpx.post(
            f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user.keycloak_user_id}/verify-otp",
            json={"otp": data.otp_code}
        )
        
        if otp_response.status_code != 200:
            return error(message="OTP incorrecto")
    
    # 3. Actualizar contraseña
    user.password_hash = bcrypt.hash(data.new_password)
    db.commit()
    
    # 4. Enviar email de confirmación
    send_email(
        to=user.email,
        subject="Tu contraseña fue cambiada",
        body="Si no fuiste tú, resetea tu contraseña inmediatamente"
    )
    
    return {"message": "Contraseña cambiada exitosamente"}
```

---

## Ventajas y Desventajas

### ✅ Ventajas de esta Opción

#### 1. Migración Gradual

- Cambios mínimos en código existente
- No rompes flujo actual de usuarios sin 2FA
- Puedes hacer 2FA opcional inicialmente
- Los usuarios sin 2FA siguen usando tu sistema actual

#### 2. Control Total

- Sigues siendo dueño de tu lógica de autenticación
- Tus JWT bajo tu control
- Base de datos de usuarios bajo tu control
- Flexibilidad para cambios futuros

#### 3. Flexibilidad de Migración

- Puedes cambiar Keycloak por otro servicio OTP sin refactorizar todo
- Fácil revertir si decide cambiar de estrategia
- Implementación por fases

#### 4. Menor Complejidad Infraestructural

- No necesitas migrar usuarios
- No cambias frontend dramáticamente
- Keycloak es solo un microservicio adicional
- Puedes desplegar Keycloak sin afectar sistema actual

#### 5. Usuarios Existentes No se Ven Afectados

- Usuarios actuales siguen usando login tradicional
- Si no habilitan 2FA, nada cambia para ellos
- Transición suave

---

### ❌ Desventajas de esta Opción

#### 1. Duplicación de Datos

- Usuarios existen en PostgreSQL Y Keycloak
- Sincronización manual necesaria
- Riesgo de inconsistencias entre sistemas
- Si cambias datos en PostgreSQL, Keycloak puede quedarse desactualizado

#### 2. Mayor Complejidad de Código

- Dos sistemas de auth que coordinar
- Manejo de errores duplicado
- Lógica de sincronización custom
- Más puntos de fallo

#### 3. No Aprovechas Keycloak Completo

- Pagas costo de mantener Keycloak
- Solo usas fracción de sus capacidades (OTP)
- Pierdes SSO, gestión avanzada de roles, etc.
- Potencial "overkill" de recursos

#### 4. Mantenimiento Doble

- Updates de seguridad en dos lugares
- Monitoreo de dos sistemas
- Logs distribuidos entre sistemas
- Debugging más complejo

#### 5. Latencia Adicional

- Cada login con 2FA requiere llamada externa a Keycloak
- Network hop adicional (10-100ms típicamente)
- Timeout si Keycloak cae (necesitas fallback)
- Degradación de performance durante picos

#### 6. Escalabilidad

- Más puntos de fallo
- Keycloak debe escalar con tu tráfico
- Costos de infraestructura adicionales
- Más complicado debuggear problemas distribuidos

#### 7. Dependencia Externa

- Si Keycloak se cae, login con 2FA se cae
- Requiere network connectivity a Keycloak
- Potencial problema en entornos con restricciones

---

## Consideraciones de Implementación

### Manejo de Errores

#### Si Keycloak No Responde

Decisión crítica: ¿Qué haces si Keycloak se cae?

**Opción 1: Modo Degradado**

```python
try:
    response = httpx.post(keycloak_url, timeout=5)
except (httpx.ConnectError, httpx.TimeoutException):
    logger.error("Keycloak no responde, entrando en modo degradado")
    
    # Permitir login sin 2FA? (riesgoso)
    if user.two_factor_enabled and ALLOW_DEGRADED_MODE:
        return {
            "warning": "Verificación 2FA no disponible momentáneamente",
            "access_token": generate_jwt(user)
        }
    elif not user.two_factor_enabled:
        # Usuario sin 2FA, permitir login
        return {"access_token": generate_jwt(user)}
    else:
        return error(message="Autenticación no disponible", status_code=503)
```

**Opción 2: Fallar Completamente (Más Seguro)**

```python
try:
    response = httpx.post(keycloak_url, timeout=5)
except (httpx.ConnectError, httpx.TimeoutException):
    # Registrar incidente
    send_alert_to_ops("Keycloak is down!")
    
    return error(
        message="Servicio de autenticación no disponible. Intenta más tarde",
        status_code=503
    )
```

**Opción 3: Respaldo Local**

Almacenar último secret OTP conocido localmente (riesgoso):

```python
# En tabla user:
# two_factor_backup_secret (encrypted, last known secret)

if keycloak_unavailable and user.two_factor_backup_secret:
    # Validar OTP contra secret local
    local_otp_validator = pyotp.TOTP(decrypt(user.two_factor_backup_secret))
    if local_otp_validator.verify(otp_code):
        log_warning("Validación OTP local, Keycloak estaba inaccesible")
        return jwt_response(user)
```

Riesgos: Secret podría estar desincronizado.

#### Timeout Strategy

```python
import httpx

# Crear cliente con timeout
keycloak_client = httpx.AsyncClient(
    timeout=5.0,  # 5 segundos máximo
    limits=httpx.Limits(
        max_connections=10,
        max_keepalive_connections=5
    )
)

# Retry con backoff
async def call_keycloak_with_retry(url, **kwargs):
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            response = await keycloak_client.post(url, **kwargs)
            return response
        except httpx.TimeoutException:
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # Backoff exponencial
                await asyncio.sleep(wait_time)
            else:
                raise
```

### Seguridad

#### Almacenamiento de Credentials

**CLIENT_SECRET:**

```python
# ❌ NUNCA en código
KEYCLOAK_CLIENT_SECRET = "secret123"  # Malo

# ✅ SIEMPRE en variables de entorno
import os
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

# ✅ O usar secreto manejador (AWS Secrets Manager, etc)
from aws_secrets import get_secret
KEYCLOAK_CLIENT_SECRET = get_secret("keycloak-client-secret")
```

**Validación de Tokens Temporales:**

```python
# JWT temporal firmado con secret diferente
SECRET_2FA = "separate-secret-for-2fa"  # Variable de entorno

# Cambiar secrets periódicamente
# Documentar rotación de secrets
# Usar sistema de versionado de secrets
```

#### Validación de Certificados TLS

```python
# En producción SIEMPRE verificar certificados
response = httpx.post(
    "https://keycloak.production.com/...",
    verify=True  # ✅ Verificar certificado SSL
)

# ❌ NUNCA en producción:
response = httpx.post(
    "https://keycloak.production.com/...",
    verify=False  # Peligroso
)
```

#### Límite de Reintentos

```python
CHALLENGE_MAX_ATTEMPTS = 5
CHALLENGE_LOCKOUT_MINUTES = 15

if challenge.attempts >= CHALLENGE_MAX_ATTEMPTS:
    challenge.status = "failed"
    challenge.failed_at = datetime.utcnow()
    db.commit()
    
    # Registrar intent fraudulento
    audit_log = AuditLog(
        user_id=user.id,
        event_type="2fa_brute_force",
        ip_address=request.client.host,
        status="blocked"
    )
    db.add(audit_log)
    db.commit()
    
    return error(
        message=f"Demasiados intentos. Intenta de nuevo en {CHALLENGE_LOCKOUT_MINUTES} minutos",
        status_code=429
    )
```

### Performance

#### Caching de Tokens de Servicio

```python
from functools import lru_cache
from datetime import datetime, timedelta

class KeycloakServiceToken:
    def __init__(self):
        self.token = None
        self.expires_at = None
    
    async def get_valid_token(self):
        """Obtiene token válido, reutilizando si no expiró"""
        
        if self.token and datetime.utcnow() < self.expires_at:
            return self.token  # Reutilizar
        
        # Token expiró, obtener uno nuevo
        response = await httpx.post(
            f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token",
            data={
                "grant_type": "client_credentials",
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET
            }
        )
        
        data = response.json()
        self.token = data["access_token"]
        self.expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"] - 60)
        
        return self.token

# Usar singleton
_keycloak_service_token = KeycloakServiceToken()

async def get_service_token():
    return await _keycloak_service_token.get_valid_token()
```

#### Connection Pooling

```python
# Crear cliente con pool
keycloak_client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=20,  # Pool size
        max_keepalive_connections=10
    ),
    timeout=httpx.Timeout(10.0, connect=5.0)
)

# Usar en app
app.keycloak_client = keycloak_client

# Cleanup en shutdown
@app.on_event("shutdown")
async def shutdown():
    await app.keycloak_client.aclose()
```

#### Async Operations

```python
# ❌ Bloquear el servidor
@router.post("/auth/verify-2fa")
def verify_2fa(data):
    # Esto bloquea el event loop
    response = requests.post(keycloak_url)  # requests es bloqueante
    return response

# ✅ Usar async
@router.post("/auth/verify-2fa")
async def verify_2fa(data):
    # No bloquea el event loop
    response = await keycloak_client.post(keycloak_url)
    return response
```

#### Background Tasks

```python
from fastapi import BackgroundTasks

@router.post("/auth/register")
async def register(data: RegisterRequest, background_tasks: BackgroundTasks):
    # Crear usuario
    user = create_user(data)
    
    # Sincronizar con Keycloak en background
    background_tasks.add_task(sync_user_to_keycloak, user.id)
    
    # Responder inmediatamente al cliente
    return {"user_id": user.id, "message": "Registrado"}

async def sync_user_to_keycloak(user_id):
    """Ejecuta en background sin bloquear respuesta"""
    user = get_user(user_id)
    httpx.post(keycloak_url, json=...)
```

---

## Comparación con Alternativas

### Opción 1: Keycloak Completo (Reemplazo Total)

**Diferencias principales:**

| Aspecto | Opción 2 (Híbrida) | Opción 1 (Completa) |
|--------|-------------------|-------------------|
| **Gestión de usuarios** | Tu DB (PostgreSQL) | Keycloak |
| **Generación JWT** | Tu gateway | Keycloak |
| **Datos de usuario** | En PostgreSQL | En Keycloak |
| **Tokens** | Tus JWT propios | Tokens OpenID Connect |
| **Cambios en código** | Moderados | Sustanciales |
| **Compatibilidad reversa** | Alta (2FA opcional) | Baja (cambio total) |
| **SSO** | No | Sí |
| **Recursos requeridos** | Menores | Mayores |
| **Complejidad** | Media | Alta |

**Cuándo elegir Opción 1:**

- Planeas migrar toda auth a Keycloak
- Necesitas SSO multi-aplicación
- Requieres gestión avanzada de roles/permisos
- Presupuesto para infraestructura

### Alternativa Simple: TOTP Nativo (Sin Keycloak)

**Implementación con librería `pyotp`:**

```python
# En requirements.txt
pyotp==2.9.0
qrcode==7.4.2
```

**Flujo:**

1. Usuario habilita 2FA
2. Tu gateway genera secret OTP local
3. Generas QR con `qrcode` library
4. Usuario escanea con Google Authenticator
5. Tu gateway almacena secret en PostgreSQL (encriptado)
6. En login con 2FA, validas OTP localmente con `pyotp`

```python
import pyotp
from cryptography.fernet import Fernet

# Generar secret
secret = pyotp.random_base32()

# Generar QR
totp = pyotp.TOTP(secret)
qr_uri = totp.provisioning_uri(
    name="jugador123@videogames-api",
    issuer_name="Videogames API"
)

# Encriptar y guardar en BD
cipher_suite = Fernet(ENCRYPTION_KEY)
encrypted_secret = cipher_suite.encrypt(secret.encode())
user.two_factor_secret = encrypted_secret
db.commit()

# Validar OTP
user_secret = cipher_suite.decrypt(user.two_factor_secret).decode()
totp = pyotp.TOTP(user_secret)

if totp.verify(otp_code):
    return jwt_response(user)
else:
    return error("OTP inválido")
```

**Ventajas:**

- ✅ Muy simple
- ✅ Sin dependencias externas complejas
- ✅ Sin latencia de red
- ✅ Todo en tu control
- ✅ Bajo costo infraestructural

**Desventajas:**

- ❌ Solo TOTP (no SMS, WebAuthn, etc.)
- ❌ Implementas todo desde cero
- ❌ Sin UI de gestión Keycloak
- ❌ Menos profesional/audit logs limitados
- ❌ No escalable para múltiples aplicaciones

**Cuándo elegir TOTP nativo:**

- MVP o prototipo rápido
- Solo necesitas TOTP básico
- Quieres minimizar complejidad
- Presupuesto muy limitado
- Team pequeño

---

## Conclusiones y Decisiones

### Árbol de Decisión

```
¿Necesitas 2FA?
├─ NO → Mantén tu sistema actual
│
└─ SÍ
   ├─ ¿Solo TOTP o múltiples métodos?
   │  ├─ Solo TOTP → TOTP Nativo (más simple)
   │  └─ Múltiples → Sigue leyendo...
   │
   ├─ ¿Timeline de implementación?
   │  ├─ Rápido (semanas) → TOTP Nativo o Opción 2 Híbrida
   │  └─ Lento (meses) → Opción 1 Completa
   │
   ├─ ¿Presupuesto infraestructural?
   │  ├─ Limitado → TOTP Nativo
   │  ├─ Moderado → Opción 2 Híbrida
   │  └─ Amplio → Opción 1 Completa
   │
   └─ ¿Planes futuros de SSO?
      ├─ NO → TOTP Nativo
      ├─ Posiblemente → Opción 2 Híbrida
      └─ SÍ seguro → Opción 1 Completa
```

### Recomendación Final

Para tu proyecto (API Gateway AUTH):

**Recomendación: Opción 2 Híbrida con Keycloak**

Razones:

1. **Balance perfecto**: Cambios moderados sin rewrite total
2. **Escalabilidad**: Si creces, puedes migrar a Opción 1
3. **Professional**: Keycloak proporciona robustez enterprise
4. **Flexibilidad**: 2FA opcional permite rollout gradual
5. **Futuro**: Prepara el terreno para SSO si lo necesitas
6. **Team**: Apropiadopara equipo mediano

---

**Fin de documento**

Generado: 4 de noviembre de 2025
Versión: 1.0
