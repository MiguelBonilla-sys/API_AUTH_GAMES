# Plan de Implementación OTP/TOTP con Keycloak

## ✅ Estado de Implementación

### Completado

1. ✅ **Modelo User actualizado** - Campos 2FA agregados
2. ✅ **Configuración Settings** - Variables de Keycloak agregadas
3. ✅ **Servicio Keycloak** - `keycloak_service.py` creado
4. ✅ **Schemas 2FA** - Schemas de request/response creados
5. ✅ **Endpoints 2FA** - Todos los endpoints implementados:
   - `/auth/enable-2fa` - Habilitar 2FA
   - `/auth/confirm-2fa` - Confirmar configuración
   - `/auth/verify-2fa` - Verificar código OTP en login
   - `/auth/2fa/status` - Obtener estado de 2FA
   - `/auth/disable-2fa` - Deshabilitar 2FA
6. ✅ **Login modificado** - Detecta y maneja 2FA
7. ✅ **JWT Handler** - Funciones para tokens temporales 2FA

### Completado (Continuación)

8. ✅ **Migración de Base de Datos** - Campos 2FA agregados a la tabla users

### Pendiente

1. ⚠️ **Validación OTP real** - Implementar validación con Keycloak o pyotp (actualmente es placeholder)
2. ⚠️ **Variables de entorno en Railway** - Configurar en producción
3. ⚠️ **Configuración Keycloak** - Asignar roles al Service Account y configurar OTP Policy

---

## 📋 Pasos para Completar la Implementación

### Paso 1: Crear y Ejecutar Migración de Base de Datos ✅ COMPLETADO

```bash
# ✅ Migración creada y ejecutada exitosamente
# Archivo: alembic/versions/3d6781569585_add_two_factor_fields.py
# Campos agregados:
# - two_factor_enabled (Boolean, default=False)
# - two_factor_method (String(50), nullable)
# - keycloak_user_id (String(36), nullable, indexed)
# - two_factor_configured_at (DateTime, nullable)
```

### Paso 2: Configurar Variables de Entorno en Railway

En tu servicio de API Gateway en Railway, agrega:

```bash
KEYCLOAK_SERVER_URL=https://keycloak-production-a4e7.up.railway.app
KEYCLOAK_REALM=master
KEYCLOAK_CLIENT_ID=api-gateway-2fa-service
KEYCLOAK_CLIENT_SECRET=C0s3BSKl6iC1HnLckmidtcGZfFHaUTkC
TWO_FACTOR_SECRET_KEY=tu-secret-para-tokens-2fa-minimo-32-caracteres-seguro
TWO_FACTOR_TOKEN_EXPIRY_MINUTES=10
TWO_FACTOR_MAX_ATTEMPTS=5
```

### Paso 3: Configurar Keycloak (Ya completado parcialmente)

1. ✅ Cliente creado: `api-gateway-2fa-service`
2. ⚠️ **Pendiente**: Asignar roles al Service Account:
   - Ve a: Clients → `api-gateway-2fa-service` → Service account roles
   - Asignar: `manage-users`, `view-users`, `query-users` del realm `realm-management`
3. ⚠️ **Pendiente**: Configurar OTP Policy:
   - Authentication → Policies → OTP Policy
   - Type: `Time-based (TOTP)`
   - Algorithm: `SHA256`
   - Digits: `6`
   - Period: `30` segundos

### Paso 4: Mejorar Validación OTP (Opcional pero Recomendado)

Actualmente, la validación OTP es un placeholder. Para producción, implementa una de estas opciones:

**Opción A: Usar pyotp (Recomendado)**
```bash
pip install pyotp
```

Luego modificar `verify_2fa` y `confirm_2fa` para validar el código usando el secret obtenido de Keycloak.

**Opción B: Validar con Keycloak Token Endpoint**
Usar el flujo de autenticación completo de Keycloak para validar el OTP.

---

## 🔄 Flujo de Autenticación con 2FA

### Flujo Normal (Sin 2FA)
```
1. POST /auth/login {email, password}
   → 200 OK {access_token, refresh_token, user}
```

### Flujo con 2FA
```
1. POST /auth/login {email, password}
   → 200 OK {requires_2fa: true, temp_token, expires_in}

2. POST /auth/verify-2fa {temp_token, otp_code}
   → 200 OK {access_token, refresh_token, user}
```

### Habilitar 2FA
```
1. POST /auth/enable-2fa (con Bearer token)
   → 200 OK {qr_code, manual_entry_key, message}

2. Usuario escanea QR con Google Authenticator

3. POST /auth/confirm-2fa {otp_code} (con Bearer token)
   → 200 OK {two_factor_enabled: true, ...}
```

---

## 📝 Endpoints Implementados

### POST `/auth/enable-2fa`
- **Autenticación**: Requerida (Bearer token)
- **Descripción**: Genera QR code para configurar 2FA
- **Respuesta**: QR code, manual entry key, secret

### POST `/auth/confirm-2fa`
- **Autenticación**: Requerida (Bearer token)
- **Body**: `{otp_code: "123456"}`
- **Descripción**: Confirma configuración verificando un código OTP
- **Respuesta**: Estado de 2FA habilitado

### POST `/auth/verify-2fa`
- **Autenticación**: No requerida (usa temp_token)
- **Body**: `{temp_token: "...", otp_code: "123456"}`
- **Descripción**: Verifica código OTP y completa login
- **Respuesta**: Tokens de acceso completos

### GET `/auth/2fa/status`
- **Autenticación**: Requerida (Bearer token)
- **Descripción**: Obtiene estado de 2FA del usuario
- **Respuesta**: Estado de 2FA

### DELETE `/auth/disable-2fa`
- **Autenticación**: Requerida (Bearer token)
- **Descripción**: Deshabilita 2FA para el usuario
- **Respuesta**: Confirmación

---

## ⚠️ Notas Importantes

1. **Validación OTP**: Actualmente es un placeholder. Implementa validación real antes de producción.

2. **Secret de Tokens 2FA**: Asegúrate de usar un secret diferente para tokens temporales 2FA (`TWO_FACTOR_SECRET_KEY`).

3. **Keycloak Service Account**: Debe tener permisos `manage-users` para crear usuarios y configurar OTP.

4. **Migración de BD**: Ejecuta la migración antes de desplegar a producción.

5. **Testing**: Prueba todos los flujos antes de producción:
   - Login sin 2FA
   - Habilitar 2FA
   - Login con 2FA
   - Deshabilitar 2FA

---

## 🚀 Próximos Pasos

1. Ejecutar migración de base de datos
2. Configurar variables de entorno en Railway
3. Completar configuración en Keycloak (roles y OTP policy)
4. Implementar validación OTP real
5. Probar flujo completo
6. Desplegar a producción

