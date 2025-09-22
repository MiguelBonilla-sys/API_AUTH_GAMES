#!/usr/bin/env python3
"""
Script para probar los endpoints de proxy (videojuegos y desarrolladoras)
"""

import asyncio
import httpx
import json

async def test_proxy_endpoints():
    """
    Probar los endpoints de proxy que conectan con la Flask API
    """
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔗 Probando Endpoints de PROXY...")
        print(f"Base URL: {base_url}")
        print("=" * 60)
        
        # 1. Login para obtener token
        print("📡 1. Haciendo login para obtener token...")
        login_data = {
            "email": "admin@test.com",
            "password": "AdminPassword123!"
        }
        
        token = None
        try:
            response = await client.post(f"{base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                token = data['data']['access_token']
                print("   ✅ Login exitoso")
            else:
                print(f"   ❌ Error en login: {response.status_code}")
                return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        print("-" * 40)
        
        # 2. Probar endpoints de proxy
        proxy_endpoints = [
            "/api/videojuegos/",
            "/api/videojuegos/1", 
            "/api/videojuegos/categorias/",
            "/api/videojuegos/estadisticas/",
            "/api/desarrolladoras/",
            "/api/desarrolladoras/1"
        ]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        for endpoint in proxy_endpoints:
            print(f"📡 2. Probando PROXY: {endpoint}")
            try:
                response = await client.get(
                    f"{base_url}{endpoint}",
                    headers=headers
                )
                
                status_icon = "✅" if response.status_code < 400 else "❌"
                print(f"   {status_icon} Status: {response.status_code}")
                
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        if response.status_code < 400:
                            print(f"   📊 Success: {data.get('success', 'N/A')}")
                            print(f"   📝 Message: {data.get('message', 'N/A')}")
                            if 'data' in data:
                                data_content = data['data']
                                if isinstance(data_content, list):
                                    print(f"   📈 Items: {len(data_content)}")
                                    # Mostrar campos del primer item
                                    if data_content and isinstance(data_content[0], dict):
                                        print(f"   🔑 Campos: {list(data_content[0].keys())}")
                                elif isinstance(data_content, dict):
                                    print(f"   🔑 Keys: {list(data_content.keys())}")
                            if 'count' in data:
                                print(f"   📊 Count: {data['count']}")
                        else:
                            print(f"   ❌ Error: {data.get('message', 'Unknown error')}")
                    except json.JSONDecodeError:
                        print(f"   ⚠️ No JSON válido")
                        print(f"   📄 Raw: {response.text[:100]}...")
                else:
                    print(f"   📄 Content-Type: {response.headers.get('content-type')}")
                    print(f"   📄 Text: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print("-" * 40)
        
        # 3. Probar también como usuario regular
        print("\n" + "=" * 60)
        print("📡 3. Probando como USUARIO REGULAR...")
        
        # Registrar usuario regular
        register_data = {
            "email": "user@test.com",
            "password": "UserPassword123!",
            "confirm_password": "UserPassword123!",
            "role": "user"
        }
        
        try:
            response = await client.post(f"{base_url}/auth/register", json=register_data)
            if response.status_code == 409:
                print("   ℹ️ Usuario regular ya existe")
            elif response.status_code in [200, 201]:
                print("   ✅ Usuario regular registrado")
        except:
            pass
        
        # Login usuario regular
        login_data = {
            "email": "user@test.com",
            "password": "UserPassword123!"
        }
        
        user_token = None
        try:
            response = await client.post(f"{base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                user_token = data['data']['access_token']
                print("   ✅ Login como user exitoso")
        except Exception as e:
            print(f"   ❌ Error en login user: {e}")
        
        if user_token:
            user_headers = {"Authorization": f"Bearer {user_token}"}
            
            # Probar lectura (debe funcionar)
            print(f"📡 Usuario regular probando: /api/videojuegos/")
            try:
                response = await client.get(f"{base_url}/api/videojuegos/", headers=user_headers)
                status_icon = "✅" if response.status_code < 400 else "❌"
                print(f"   {status_icon} Status: {response.status_code}")
                
                if response.status_code < 400:
                    data = response.json()
                    print(f"   📈 Items: {data.get('count', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_proxy_endpoints())
