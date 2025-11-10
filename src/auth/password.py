"""
Módulo para manejo de contraseñas con bcrypt.
Implementa hash y verificación de contraseñas de forma segura.
"""

from passlib.context import CryptContext
import os

# Configuración de bcrypt
# Usar mínimo 12 rounds para seguridad (recomendado por OWASP)
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# Contexto de encriptación
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=BCRYPT_ROUNDS
)


def hash_password(password: str) -> str:
    """
    Generar hash de contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar contraseña contra su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado en la base de datos
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_strength(password: str) -> dict:
    """
    Evaluar la fortaleza de una contraseña.
    
    Args:
        password: Contraseña a evaluar
        
    Returns:
        Diccionario con información sobre la fortaleza
    """
    strength = {
        "length": len(password),
        "has_uppercase": any(c.isupper() for c in password),
        "has_lowercase": any(c.islower() for c in password),
        "has_digits": any(c.isdigit() for c in password),
        "has_special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password),
        "score": 0
    }
    
    # Calcular score de fortaleza
    if strength["length"] >= 8:
        strength["score"] += 1
    if strength["length"] >= 12:
        strength["score"] += 1
    if strength["has_uppercase"]:
        strength["score"] += 1
    if strength["has_lowercase"]:
        strength["score"] += 1
    if strength["has_digits"]:
        strength["score"] += 1
    if strength["has_special"]:
        strength["score"] += 1
    
    return strength


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validar que una contraseña cumpla con los requisitos mínimos.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Tupla (es_válida, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    strength = get_password_strength(password)
    
    if strength["score"] < 3:
        return False, "La contraseña debe contener al menos: una mayúscula, una minúscula y un número"
    
    return True, ""
