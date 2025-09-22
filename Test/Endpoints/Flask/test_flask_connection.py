#!/usr/bin/env python3
"""
Script para probar la conectividad a la API Flask
"""

import asyncio
import httpx
import json

async def test_flask_api():
    """
    Probar conectividad con la API Flask externa
    """
    base_url = "https://flaskapi-production-a966.up.railway.app"
    
    endpoints_to_test = [
        "/api/videojuegos/",
        "/api/desarrolladoras/"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔗 Probando conectividad con la API Flask...")
        print(f"Base URL: {base_url}")
        print("-" * 60)
        
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            
            try:
                print(f"📡 Probando: {endpoint}")
                response = await client.get(url)
                
                print(f"   ✅ Status: {response.status_code}")
                
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"   📊 Claves en respuesta: {list(data.keys())}")
                            if 'data' in data:
                                print(f"   📝 Tipo de data: {type(data['data'])}")
                                if isinstance(data['data'], list) and data['data']:
                                    print(f"   📈 Items en data: {len(data['data'])}")
                    except json.JSONDecodeError:
                        print("   ⚠️  Respuesta no es JSON válido")
                else:
                    print(f"   📄 Content-Type: {response.headers.get('content-type', 'no definido')}")
                    
            except httpx.TimeoutException:
                print(f"   ❌ Timeout al conectar con {endpoint}")
            except httpx.ConnectError:
                print(f"   ❌ Error de conexión con {endpoint}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_flask_api())
