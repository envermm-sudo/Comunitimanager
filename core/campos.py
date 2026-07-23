from django.db import models
from core.cifrado import cifrar, descifrar


class CampoCifrado(models.TextField):
    description = "Campo de texto cifrado en reposo"

    def get_prep_value(self, value):
        if value is None or value == "":
            return value
        return cifrar(str(value))

    def from_db_value(self, value, expression, connection):
        if value is None or value == " ":
            return value
        return descifrar(value)

    def to_python(self, value):
        return value
