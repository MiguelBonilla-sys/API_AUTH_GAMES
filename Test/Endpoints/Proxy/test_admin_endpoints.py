#!/usr/bin/env python3
"""
Script para probar los endpoints de administración
"""

import asyncio
import httpx
import json

async def test_admin_endpoints():
    """
    Probar los endpoints de administración del gateway
    """
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔗 Probando Gateway de Autenticación...")
        print(f"Base URL: {base_url}")
        print("=" * 60)
        
        # 1. Verificar que el servidor esté funcionando
        try:
            print("📡 1. Probando health check...")
            response = await client.get(f"{base_url}/")
            print(f"   ✅ Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Message: {data.get('message', 'N/A')}")
            print("-" * 40)
        except Exception as e:
            print(f"   ❌ Error en health check: {e}")
            return
        
        # 2. Intentar registrar un usuario admin
        print("📡 2. Registrando usuario admin...")
        register_data = {
            "email": "admin@test.com",
            "password": "AdminPassword123!",
            "confirm_password": "AdminPassword123!",
            "role": "admin"
        }
        
        try:
            response = await client.post(
                f"{base_url}/auth/register", 
                json=register_data
            )
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print("   ✅ Usuario admin registrado")
            elif response.status_code == 409:
                print("   ℹ️ Usuario admin ya existe")
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                print(f"   ⚠️ Respuesta: {data}")
        except Exception as e:
            print(f"   ❌ Error en registro: {e}")
        
        print("-" * 40)
        
        # 3. Intentar hacer login
        print("📡 3. Haciendo login como admin...")
        login_data = {
            "email": "admin@test.com",
            "password": "AdminPassword123!"
        }
        
        token = None
        try:
            response = await client.post(
                f"{base_url}/auth/login", 
                json=login_data
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('access_token'):
                    token = data['data']['access_token']
                    print("   ✅ Login exitoso")
                    print(f"   🔑 Token obtenido: {token[:20]}...")
                else:
                    print(f"   ⚠️ Login response: {data}")
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                print(f"   ❌ Error en login: {data}")
        except Exception as e:
            print(f"   ❌ Error en login: {e}")
        
        print("-" * 40)
        
        if not token:
            print("❌ No se pudo obtener token, terminando pruebas...")
            return
        
        # 4. Probar endpoints de admin
        admin_endpoints = [
            "/admin/users",
            "/admin/roles", 
            "/admin/stats"
        ]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        for endpoint in admin_endpoints:
            print(f"📡 4. Probando: {endpoint}")
            try:
                response = await client.get(
                    f"{base_url}{endpoint}",
                    headers=headers
                )
                
                status_icon = "✅" if response.status_code < 400 else "❌"
                print(f"   {status_icon} Status: {response.status_code}")
                
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    if response.status_code < 400:
                        print(f"   📊 Success: {data.get('success', 'N/A')}")
                        print(f"   📝 Message: {data.get('message', 'N/A')}")
                        if 'data' in data:
                            data_content = data['data']
                            if isinstance(data_content, list):
                                print(f"   📈 Items: {len(data_content)}")
                            elif isinstance(data_content, dict):
                                print(f"   🔑 Keys: {list(data_content.keys())}")
                    else:
                        print(f"   ❌ Error: {data.get('message', 'Unknown error')}")
                        if 'detail' in data:
                            print(f"   📋 Detail: {data['detail']}")
                else:
                    print(f"   📄 Text: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_admin_endpoints())
