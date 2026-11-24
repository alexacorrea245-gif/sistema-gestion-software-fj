"""Clase abstracta base para las entidades generales del sistema."""
from abc import ABC, abstractmethod
from itertools import count


class EntidadBase(ABC):
    """Representa cualquier entidad del sistema (cliente, servicio, reserva).

    Aporta un identificador único autogenerado y obliga a las clases
    hijas a implementar ``describir`` (abstracción + polimorfismo).
    """

    _contadores: dict = {}  # un contador independiente por categoría (CLI, SRV, RES)
    _CATEGORIA = "ENT"  # las clases hijas sobrescriben este valor

    def __init__(self) -> None:
        # El id se asigna al final de la construcción (ver _asignar_id), de modo
        # que un objeto inválido no consuma números de la secuencia.
        self._id = 0

    def _asignar_id(self) -> None:
        """Asigna el siguiente identificador de la categoría de la clase."""
        contador = EntidadBase._contadores.setdefault(self._CATEGORIA, count(1))
        self._id = next(contador)

    @property
    def id(self) -> int:
        """Identificador único de la entidad (solo lectura)."""
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""

    def __str__(self) -> str:
        return self.describir()
