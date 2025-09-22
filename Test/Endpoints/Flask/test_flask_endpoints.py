#!/usr/bin/env python3
"""
Script para probar diferentes endpoints de la API Flask
"""

import asyncio
import httpx
import json

async def test_flask_endpoints():
    """
    Probar diferentes endpoints de la API Flask
    """
    base_url = "https://flaskapi-production-a966.up.railway.app"
    
    # Endpoints comunes a probar
    endpoints_to_test = [
        "/",
        "/health",
        "/status", 
        "/api/",
        "/api/v1/videojuegos/",
        "/videojuegos/",
        "/desarrolladoras/",
        "/api/v1/desarrolladoras/"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔗 Probando diferentes endpoints de la API Flask...")
        print(f"Base URL: {base_url}")
        print("=" * 60)
        
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            
            try:
                print(f"📡 Probando: {endpoint}")
                response = await client.get(url)
                
                status_icon = "✅" if response.status_code < 400 else "⚠️"
                print(f"   {status_icon} Status: {response.status_code}")
                
                # Ver el contenido si es exitoso
                if response.status_code < 400:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        try:
                            data = response.json()
                            print(f"   📊 Respuesta JSON:")
                            if isinstance(data, dict):
                                for key, value in data.items():
                                    if isinstance(value, str) and len(value) > 50:
                                        print(f"      {key}: {value[:50]}...")
                                    else:
                                        print(f"      {key}: {value}")
                            else:
                                print(f"      Tipo: {type(data)}")
                        except json.JSONDecodeError:
                            print("   ⚠️  Respuesta no es JSON válido")
                    else:
                        # Mostrar texto plano (truncado)
                        text = response.text[:200]
                        print(f"   📄 Texto: {text}...")
                
            except httpx.TimeoutException:
                print(f"   ❌ Timeout al conectar con {endpoint}")
            except httpx.ConnectError:
                print(f"   ❌ Error de conexión con {endpoint}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_flask_endpoints())
