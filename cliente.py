"""Clase Cliente con validaciones robustas y datos encapsulados."""
import re

from .entidades import EntidadBase
from .excepciones import ClienteInvalidoError, ParametroFaltanteError

# Expresiones regulares usadas en las validaciones
_PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
_PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,60}$")


class Cliente(EntidadBase):
    """Cliente de Software FJ. Sus datos personales son privados."""

    _CATEGORIA = "CLI"

    def __init__(self, nombre, documento, correo, telefono) -> None:
        super().__init__()
        # Cada asignación pasa por el setter, que valida el dato
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        self._asignar_id()  # solo si todas las validaciones pasaron

    @staticmethod
    def _requerido(valor, campo: str) -> str:
        """Verifica que el dato exista y no sea una cadena vacía."""
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError(f"Falta el parámetro obligatorio '{campo}'.")
        return str(valor).strip()

    # ---------------- nombre ----------------
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor) -> None:
        valor = self._requerido(valor, "nombre")
        if not _PATRON_NOMBRE.match(valor):
            raise ClienteInvalidoError(f"Nombre inválido: '{valor}'.")
        self._nombre = valor.title()

    # ---------------- documento ----------------
    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor) -> None:
        valor = self._requerido(valor, "documento")
        if not valor.isdigit() or not 6 <= len(valor) <= 12:
            raise ClienteInvalidoError(
                f"Documento inválido '{valor}': debe tener entre 6 y 12 dígitos."
            )
        self._documento = valor

    # ---------------- correo ----------------
    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor) -> None:
        valor = self._requerido(valor, "correo")
        if not _PATRON_CORREO.match(valor):
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.lower()

    # ---------------- teléfono ----------------
    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor) -> None:
        valor = self._requerido(valor, "telefono")
        if not valor.isdigit() or len(valor) != 10:
            raise ClienteInvalidoError(
                f"Teléfono inválido '{valor}': debe tener exactamente 10 dígitos."
            )
        self._telefono = valor

    def describir(self) -> str:
        """Descripción del cliente (polimorfismo de EntidadBase)."""
        return f"Cliente #{self.id}: {self.nombre} | Doc: {self.documento} | {self.correo}"
