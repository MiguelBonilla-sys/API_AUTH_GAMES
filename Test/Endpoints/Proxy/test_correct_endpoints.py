#!/usr/bin/env python3
"""
Script para probar los endpoints correctos de la API Flask
"""

import asyncio
import httpx
import json

async def test_correct_flask_endpoints():
    """
    Probar los endpoints correctos de la API Flask
    """
    base_url = "https://flaskapi-production-a966.up.railway.app"
    
    # Endpoints correctos según el usuario
    endpoints_to_test = [
        "/api/videojuegos",
        "/api/desarrolladoras"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔗 Probando endpoints CORRECTOS de la API Flask...")
        print(f"Base URL: {base_url}")
        print("=" * 60)
        
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            
            try:
                print(f"📡 Probando: {endpoint}")
                response = await client.get(url)
                
                status_icon = "✅" if response.status_code < 400 else "⚠️"
                print(f"   {status_icon} Status: {response.status_code}")
                
                # Mostrar headers importantes
                print(f"   📋 Content-Type: {response.headers.get('content-type', 'no definido')}")
                print(f"   📏 Content-Length: {response.headers.get('content-length', 'no definido')}")
                
                # Ver el contenido
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        print(f"   📊 Respuesta JSON:")
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if key == 'data' and isinstance(value, list):
                                    print(f"      {key}: Lista con {len(value)} elementos")
                                    if value and len(value) > 0:
                                        # Mostrar primer elemento como ejemplo
                                        first_item = value[0]
                                        if isinstance(first_item, dict):
                                            print(f"         Ejemplo: {list(first_item.keys())}")
                                elif isinstance(value, str) and len(value) > 50:
                                    print(f"      {key}: {value[:50]}...")
                                else:
                                    print(f"      {key}: {value}")
                        else:
                            print(f"      Tipo: {type(data)}, Valor: {str(data)[:100]}...")
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️  Error JSON: {e}")
                        print(f"   📄 Raw text (primeros 200 chars): {response.text[:200]}...")
                else:
                    # Mostrar texto plano (truncado)
                    text = response.text[:300]
                    print(f"   📄 Texto: {text}")
                    if len(response.text) > 300:
                        print("      ...")
                
            except httpx.TimeoutException:
                print(f"   ❌ Timeout al conectar con {endpoint}")
            except httpx.ConnectError:
                print(f"   ❌ Error de conexión con {endpoint}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_correct_flask_endpoints())
