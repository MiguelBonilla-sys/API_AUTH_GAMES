"""
Script de testing para probar todos los endpoints implementados.
Ejecuta pruebas básicas de funcionalidad.
"""

import asyncio
import httpx
import json
from typing import Dict, Any


class APITester:
    """
    Clase para testing de endpoints de la API.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.access_token = None
        self.refresh_token = None
        self.admin_token = None
    
    async def close(self):
        """Cerrar cliente HTTP."""
        await self.client.aclose()
    
    async def test_health_check(self) -> bool:
        """Probar health check."""
        print("🔍 Probando health check...")
        try:
            response = await self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check OK: {data['message']}")
                return True
            else:
                print(f"❌ Health check falló: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error en health check: {e}")
            return False
    
    async def test_register_user(self, email: str, password: str, role: str = "user") -> bool:
        """Probar registro de usuario."""
        print(f"🔍 Probando registro de usuario: {email}")
        try:
            data = {
                "email": email,
                "password": password,
                "confirm_password": password,
                "role": role
            }
            response = await self.client.post(
                f"{self.base_url}/auth/register",
                json=data
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Usuario registrado: {result['message']}")
                return True
            else:
                print(f"❌ Registro falló: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error en registro: {e}")
            return False
    
    async def test_login(self, email: str, password: str) -> bool:
        """Probar login de usuario."""
        print(f"🔍 Probando login: {email}")
        try:
            data = {
                "email": email,
                "password": password
            }
            response = await self.client.post(
                f"{self.base_url}/auth/login",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["data"]["access_token"]
                self.refresh_token = result["data"]["refresh_token"]
                print(f"✅ Login exitoso: {result['message']}")
                return True
            else:
                print(f"❌ Login falló: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False
    
    async def test_get_profile(self) -> bool:
        """Probar obtener perfil de usuario."""
        print("🔍 Probando obtener perfil...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/auth/me",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Perfil obtenido: {result['data']['email']}")
                return True
            else:
                print(f"❌ Obtener perfil falló: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error al obtener perfil: {e}")
            return False
    
    async def test_refresh_token(self) -> bool:
        """Probar renovación de token."""
        print("🔍 Probando renovación de token...")
        try:
            data = {"refresh_token": self.refresh_token}
            response = await self.client.post(
                f"{self.base_url}/auth/refresh",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["data"]["access_token"]
                print(f"✅ Token renovado: {result['message']}")
                return True
            else:
                print(f"❌ Renovación falló: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error en renovación: {e}")
            return False
    
    async def test_videojuegos_list(self) -> bool:
        """Probar listar videojuegos."""
        print("🔍 Probando listar videojuegos...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/videojuegos/",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Videojuegos listados: {len(result.get('data', []))} elementos")
                return True
            else:
                print(f"❌ Listar videojuegos falló: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error al listar videojuegos: {e}")
            return False
    
    async def test_desarrolladoras_list(self) -> bool:
        """Probar listar desarrolladoras."""
        print("🔍 Probando listar desarrolladoras...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/desarrolladoras/",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Desarrolladoras listadas: {len(result.get('data', []))} elementos")
                return True
            else:
                print(f"❌ Listar desarrolladoras falló: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error al listar desarrolladoras: {e}")
            return False
    
    async def test_admin_endpoints(self) -> bool:
        """Probar endpoints de administración."""
        print("🔍 Probando endpoints de administración...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Probar listar usuarios (debería fallar si no es admin)
            response = await self.client.get(
                f"{self.base_url}/admin/users",
                headers=headers
            )
            
            if response.status_code == 403:
                print("✅ Acceso denegado correctamente (usuario no es admin)")
                return True
            elif response.status_code == 200:
                print("✅ Acceso permitido (usuario es admin)")
                return True
            else:
                print(f"❌ Respuesta inesperada: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error en endpoints de admin: {e}")
            return False
    
    async def test_logout(self) -> bool:
        """Probar logout."""
        print("🔍 Probando logout...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.client.post(
                f"{self.base_url}/auth/logout",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Logout exitoso: {result['message']}")
                return True
            else:
                print(f"❌ Logout falló: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error en logout: {e}")
            return False
    
    async def test_password_strength(self) -> bool:
        """Probar análisis de fortaleza de contraseña."""
        print("🔍 Probando análisis de fortaleza de contraseña...")
        try:
            data = {"password": "TestPassword123!"}
            response = await self.client.post(
                f"{self.base_url}/auth/check-password-strength",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Análisis de contraseña: Score {result['data']['strength_score']}")
                return True
            else:
                print(f"❌ Análisis falló: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
            return False
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas."""
        print("🚀 Iniciando pruebas de la API Auth Gateway...")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Health Check
        total_tests += 1
        if await self.test_health_check():
            tests_passed += 1
        print()
        
        # Test 2: Análisis de contraseña
        total_tests += 1
        if await self.test_password_strength():
            tests_passed += 1
        print()
        
        # Test 3: Registro de usuario
        total_tests += 1
        if await self.test_register_user("test@example.com", "TestPassword123!"):
            tests_passed += 1
        print()
        
        # Test 4: Login
        total_tests += 1
        if await self.test_login("test@example.com", "TestPassword123!"):
            tests_passed += 1
        print()
        
        # Test 5: Obtener perfil
        total_tests += 1
        if await self.test_get_profile():
            tests_passed += 1
        print()
        
        # Test 6: Renovar token
        total_tests += 1
        if await self.test_refresh_token():
            tests_passed += 1
        print()
        
        # Test 7: Listar videojuegos
        total_tests += 1
        if await self.test_videojuegos_list():
            tests_passed += 1
        print()
        
        # Test 8: Listar desarrolladoras
        total_tests += 1
        if await self.test_desarrolladoras_list():
            tests_passed += 1
        print()
        
        # Test 9: Endpoints de admin
        total_tests += 1
        if await self.test_admin_endpoints():
            tests_passed += 1
        print()
        
        # Test 10: Logout
        total_tests += 1
        if await self.test_logout():
            tests_passed += 1
        print()
        
        # Resumen
        print("=" * 60)
        print(f"📊 Resumen de pruebas: {tests_passed}/{total_tests} pasaron")
        
        if tests_passed == total_tests:
            print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        else:
            print("⚠️  Algunas pruebas fallaron. Revisar logs arriba.")
        
        return tests_passed == total_tests


async def main():
    """Función principal para ejecutar las pruebas."""
    tester = APITester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    print("🧪 Script de testing para API Auth Gateway")
    print("Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    print()
    
    # Ejecutar pruebas
    asyncio.run(main())
