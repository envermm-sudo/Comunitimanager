from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _obtener_fernet():
    clave = getattr(settings, "FERNET_KEY", None)
    if not clave:
        raise ImproperlyConfigured("Falta la variable FERNET_KEY en el archivo .env")
    return Fernet(clave.encode())


def cifrar(texto):
    if texto is None or texto == "":
        return texto
    fernet = _obtener_fernet()
    return fernet.encrypt(str(texto).encode()).decode()


def descifrar(texto_cifrado):
    if texto_cifrado is None or texto_cifrado == "":
        return texto_cifrado
    fernet = _obtener_fernet()
    try:
        return fernet.decrypt(texto_cifrado.encode()).decode()
    except InvalidToken:
        raise ValueError(
            "No se pudo descifrar el valor. Verifique que FERNET_KEY sea la correcta."
        )
