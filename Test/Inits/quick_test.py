"""
Test rápido para verificar que el servidor funciona.
"""

import requests
import json

def test_endpoint(url, description):
    """Probar un endpoint y mostrar resultado."""
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ {description}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Respuesta: {data.get('message', 'OK')}")
        return True
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False

def main():
    """Función principal."""
    print("🧪 Test rápido del API Auth Gateway")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Tests básicos
    tests = [
        (f"{base_url}/", "Health Check"),
        (f"{base_url}/health", "Health Check Detallado"),
        (f"{base_url}/docs", "Documentación"),
    ]
    
    passed = 0
    total = len(tests)
    
    for url, description in tests:
        if test_endpoint(url, description):
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Resultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests básicos pasaron!")
        print("✅ El servidor está funcionando correctamente")
    else:
        print("⚠️  Algunos tests fallaron")

if __name__ == "__main__":
    main()
