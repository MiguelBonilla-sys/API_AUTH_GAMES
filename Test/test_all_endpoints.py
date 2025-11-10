"""
Script de prueba completo para verificar login y endpoints con todos los usuarios.
Prueba cada usuario y sus permisos correspondientes.
"""

import asyncio
import httpx
import sys
import os
from typing import Dict, Optional, Union, List

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import os

# Obtener puerto de variable de entorno o usar default
PORT = int(os.getenv("PORT", 8000))
BASE_URL = f"http://localhost:{PORT}"

# Usuarios de prueba
USERS = {
    "superadmin": {
        "email": "superadmin@example.com",
        "password": "SuperAdmin123!",
        "role": "superadmin"
    },
    "editor": {
        "email": "editor@example.com",
        "password": "EditorPassword123!",
        "role": "editor"
    },
    "desarrolladora1": {
        "email": "desarrolladora1@example.com",
        "password": "DevPassword123!",
        "role": "desarrolladora"
    },
    "desarrolladora2": {
        "email": "desarrolladora2@example.com",
        "password": "DevPassword123!",
        "role": "desarrolladora"
    }
}

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def print_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")


async def login_user(client: httpx.AsyncClient, email: str, password: str) -> Optional[Dict]:
    """Hacer login y obtener token."""
    try:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                token = data["data"]["access_token"]
                user_data = data["data"]["user"]
                print_success(f"Login exitoso: {user_data['email']} ({user_data['role']})")
                return {
                    "token": token,
                    "user": user_data
                }
            else:
                print_error(f"Login falló: {data.get('message', 'Error desconocido')}")
                return None
        else:
            error_data = response.json()
            print_error(f"Login falló ({response.status_code}): {error_data.get('detail', 'Error desconocido')}")
            return None
    except Exception as e:
        print_error(f"Error al hacer login: {str(e)}")
        return None


async def test_endpoint(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    token: Optional[str] = None,
    json_data: Optional[Dict] = None,
    params: Optional[Dict] = None,
    expected_status: Union[int, List[int]] = 200,
    description: str = ""
) -> bool:
    """Probar un endpoint."""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method.upper() == "GET":
            response = await client.get(f"{BASE_URL}{endpoint}", headers=headers, params=params)
        elif method.upper() == "POST":
            response = await client.post(f"{BASE_URL}{endpoint}", headers=headers, json=json_data, params=params)
        elif method.upper() == "PUT":
            response = await client.put(f"{BASE_URL}{endpoint}", headers=headers, json=json_data)
        elif method.upper() == "DELETE":
            response = await client.delete(f"{BASE_URL}{endpoint}", headers=headers)
        else:
            print_error(f"Método HTTP no soportado: {method}")
            return False
        
        # Manejar lista de códigos esperados
        expected_codes = expected_status if isinstance(expected_status, list) else [expected_status]
        
        if response.status_code in expected_codes:
            print_success(f"{method} {endpoint} - {response.status_code} {description}")
            return True
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get("detail", f"Status {response.status_code}")
            expected_str = str(expected_codes) if len(expected_codes) > 1 else str(expected_codes[0])
            print_error(f"{method} {endpoint} - {response.status_code} (esperado {expected_str}): {detail}")
            return False
    except Exception as e:
        print_error(f"Error al probar {method} {endpoint}: {str(e)}")
        return False


async def test_public_endpoints(client: httpx.AsyncClient):
    """Probar endpoints públicos (sin autenticación)."""
    print_header("PROBANDO ENDPOINTS PÚBLICOS")
    
    results = []
    
    # Endpoints públicos de videojuegos (sin autenticación)
    public_endpoints = [
        ("GET", "/api/videojuegos/", None, None, [200, 307], "Listar videojuegos"),
        ("GET", "/api/videojuegos/categorias/", None, None, [200], "Listar categorías"),
        ("GET", "/api/videojuegos/estadisticas/", None, None, [200], "Estadísticas"),
        ("GET", "/api/videojuegos/buscar/", None, {"q": "test", "include_external": "true"}, [200], "Buscar videojuegos"),
    ]
    
    for method, endpoint, json_data, params, expected_status, description in public_endpoints:
        result = await test_endpoint(client, method, endpoint, None, json_data, params, expected_status, description)
        results.append(result)
    
    return results


async def test_user_endpoints(client: httpx.AsyncClient, user_info: Dict, role: str):
    """Probar endpoints según el rol del usuario."""
    token = user_info.get("token")
    user_email = user_info.get("user", {}).get("email", "")
    
    print_header(f"PROBANDO ENDPOINTS COMO {role.upper()} ({user_email})")
    
    results = []
    
    # Endpoints comunes para todos los usuarios autenticados
    common_endpoints = [
        ("GET", "/auth/me", None, None, 200, "Obtener perfil de usuario"),
    ]
    
    # Endpoints según rol
    if role == "superadmin":
        # Superadmin tiene acceso a todo
        role_endpoints = [
            # Videojuegos - algunos pueden fallar si no existen recursos
            ("GET", "/api/videojuegos/", None, None, [200, 307], "Listar videojuegos"),
            ("POST", "/api/videojuegos/", {"nombre": "Test Game", "categoria": "Action", "precio": 29.99, "valoracion": 8.5}, None, [201, 400, 307], "Crear videojuego"),
            ("GET", "/api/videojuegos/1/enriquecido/", None, None, [200, 404], "Obtener videojuego enriquecido"),
            ("POST", "/api/videojuegos/importar-batch/", None, {"count": 1}, [200, 201], "Importar batch videojuegos"),
            ("GET", "/api/videojuegos/sync-status/test123/", None, None, [200, 404], "Estado de sincronización"),
            
            # Desarrolladoras
            ("GET", "/api/desarrolladoras/", None, None, [200, 307], "Listar desarrolladoras"),
            ("GET", "/api/desarrolladoras/1", None, None, [200, 404], "Obtener desarrolladora por ID"),
            ("GET", "/api/desarrolladoras/1/estadisticas/", None, None, [200, 404], "Estadísticas de desarrolladora"),
            ("POST", "/api/desarrolladoras/", {"nombre": "Test Dev", "pais": "Test Country"}, None, [201, 404, 307], "Crear desarrolladora"),
            
            # Sync Logs
            ("GET", "/api/sync-logs/", None, None, [200, 307], "Listar sync logs"),
            ("GET", "/api/sync-logs/recent/", None, None, [200, 307], "Logs recientes"),
            ("GET", "/api/sync-logs/statistics/", None, None, [200, 307], "Estadísticas de sync"),
            ("GET", "/api/sync-logs/1", None, None, [200, 404], "Obtener sync log por ID"),
            
            # Admin
            ("GET", "/api/admin/users", None, None, [200, 404], "Listar usuarios"),
            ("GET", "/api/admin/roles", None, None, [200, 404], "Listar roles"),
        ]
        
    elif role == "editor":
        # Editor puede gestionar videojuegos y leer desarrolladoras
        role_endpoints = [
            # Videojuegos
            ("GET", "/api/videojuegos/", None, None, [200, 307], "Listar videojuegos"),
            ("POST", "/api/videojuegos/", {"nombre": "Test Game", "categoria": "Action", "precio": 29.99, "valoracion": 8.5}, None, [201, 400, 307], "Crear videojuego"),
            ("GET", "/api/videojuegos/1/enriquecido/", None, None, [200, 404], "Obtener videojuego enriquecido"),
            ("POST", "/api/videojuegos/importar-batch/", None, {"count": 1}, [200, 201], "Importar batch videojuegos"),
            
            # Desarrolladoras (solo lectura)
            ("GET", "/api/desarrolladoras/", None, None, [200, 307], "Listar desarrolladoras"),
            ("GET", "/api/desarrolladoras/1", None, None, [200, 404], "Obtener desarrolladora por ID"),
            ("GET", "/api/desarrolladoras/1/estadisticas/", None, None, [200, 404], "Estadísticas de desarrolladora"),
            
            # No debe tener acceso a crear/editar/eliminar desarrolladoras
            ("POST", "/api/desarrolladoras/", {"nombre": "Test Dev", "pais": "Test Country"}, None, [403], "Crear desarrolladora (debe fallar)"),
            ("PUT", "/api/desarrolladoras/1", {"nombre": "Updated Dev"}, None, [403], "Actualizar desarrolladora (debe fallar)"),
            ("DELETE", "/api/desarrolladoras/1", None, None, [403], "Eliminar desarrolladora (debe fallar)"),
            
            # Sync Logs (editor SÍ tiene acceso según el código)
            ("GET", "/api/sync-logs/", None, None, [200, 307], "Listar sync logs"),
        ]
        
    elif role == "desarrolladora":
        # Desarrolladora puede gestionar sus propios recursos
        role_endpoints = [
            # Videojuegos (sus propios)
            ("GET", "/api/videojuegos/", None, None, [200, 307], "Listar videojuegos"),
            ("POST", "/api/videojuegos/", {"nombre": "Test Game", "categoria": "Action", "precio": 29.99, "valoracion": 8.5}, None, [201, 400, 307], "Crear videojuego"),
            ("GET", "/api/videojuegos/1/enriquecido/", None, None, [200, 404], "Obtener videojuego enriquecido"),
            
            # Desarrolladoras (su propia)
            ("GET", "/api/desarrolladoras/", None, None, [200, 307], "Listar desarrolladoras"),
            ("GET", "/api/desarrolladoras/1/estadisticas/", None, None, [200, 404], "Estadísticas de desarrolladora"),
            
            # Desarrolladoras pueden importar batch (tienen VIDEOJUEGO_CREATE)
            ("POST", "/api/videojuegos/importar-batch/", None, {"count": 1}, [200, 201], "Importar batch"),
            # No debe tener acceso a sync-logs
            ("GET", "/api/sync-logs/", None, None, [403, 307], "Listar sync logs (debe fallar)"),
        ]
    
    else:
        role_endpoints = []
    
    # Probar endpoints comunes
    for method, endpoint, json_data, params, expected_status, description in common_endpoints:
        result = await test_endpoint(client, method, endpoint, token, json_data, params, expected_status, description)
        results.append(result)
    
    # Probar endpoints específicos del rol
    for endpoint_info in role_endpoints:
        method, endpoint, json_data, params, expected_status, description = endpoint_info
        
        result = await test_endpoint(client, method, endpoint, token, json_data, params, expected_status, description)
        results.append(result)
    
    return results


async def main():
    """Función principal."""
    print_header("SCRIPT DE PRUEBA COMPLETO - LOGIN Y ENDPOINTS")
    
    print_info(f"Conectando a: {BASE_URL}")
    print_info("Asegúrate de que el servidor esté ejecutándose\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Verificar que el servidor esté corriendo
        try:
            response = await client.get(f"{BASE_URL}/")
            print_success("Servidor está corriendo")
        except Exception as e:
            print_error(f"No se puede conectar al servidor: {str(e)}")
            print_warning("Asegúrate de ejecutar: uvicorn app:app --reload")
            return
        
        all_results = []
        
        # Probar endpoints públicos
        public_results = await test_public_endpoints(client)
        all_results.extend(public_results)
        
        # Probar login y endpoints para cada usuario
        user_tokens = {}
        
        for user_key, user_data in USERS.items():
            print_header(f"PROBANDO LOGIN: {user_data['email']}")
            
            login_result = await login_user(
                client,
                user_data["email"],
                user_data["password"]
            )
            
            if login_result:
                user_tokens[user_key] = login_result
                
                # Probar endpoints según el rol
                role_results = await test_user_endpoints(
                    client,
                    login_result,
                    user_data["role"]
                )
                all_results.extend(role_results)
            else:
                print_error(f"No se pudo hacer login con {user_data['email']}")
        
        # Resumen final
        print_header("RESUMEN DE PRUEBAS")
        
        total = len(all_results)
        passed = sum(1 for r in all_results if r)
        failed = total - passed
        
        print(f"\n{Colors.BOLD}Total de pruebas: {total}{Colors.RESET}")
        print_success(f"Exitosas: {passed}")
        if failed > 0:
            print_error(f"Fallidas: {failed}")
        else:
            print_success("Todas las pruebas pasaron! 🎉")
        
        print(f"\n{Colors.BOLD}Usuarios autenticados:{Colors.RESET}")
        for user_key, token_info in user_tokens.items():
            user_data = token_info.get("user", {})
            print_success(f"  - {user_data.get('email', '')} ({user_data.get('role', '')})")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nPruebas interrumpidas por el usuario")
    except Exception as e:
        print_error(f"Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()

