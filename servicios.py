"""Clase abstracta Servicio y tres servicios especializados."""
from abc import abstractmethod
from functools import singledispatchmethod

from .entidades import EntidadBase
from .excepciones import (
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)

# Códigos promocionales válidos (porcentaje de descuento)
CODIGOS_PROMO = {"PROMO10": 10.0, "VIP20": 20.0}


class Servicio(EntidadBase):
    """Clase abstracta de la que heredan todos los servicios de Software FJ."""

    _CATEGORIA = "SRV"

    def __init__(self, nombre, tarifa, disponible: bool = True) -> None:
        super().__init__()
        if nombre is None or str(nombre).strip() == "":
            raise ParametroFaltanteError("El servicio requiere un nombre.")
        if not isinstance(tarifa, (int, float)) or isinstance(tarifa, bool) or tarifa <= 0:
            raise ServicioInvalidoError(f"Tarifa inválida: {tarifa!r}. Debe ser un número > 0.")
        self._nombre = str(nombre).strip()
        self._tarifa = float(tarifa)
        self._disponible = bool(disponible)

    # --------- propiedades (encapsulación) ---------
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa(self) -> float:
        return self._tarifa

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, valor: bool) -> None:
        """Activa o desactiva el servicio."""
        self._disponible = bool(valor)

    # --------- métodos abstractos (a sobrescribir) ---------
    @abstractmethod
    def validar_parametros(self, duracion) -> None:
        """Lanza ServicioInvalidoError si la duración no es válida."""

    @abstractmethod
    def calcular_costo_base(self, duracion) -> float:
        """Costo sin impuestos ni descuentos."""

    @abstractmethod
    def describir(self) -> str:
        """Descripción específica del servicio."""

    # --------- sobrecarga de métodos ---------
    def calcular_costo(self, duracion, impuesto: float = 0.0, descuento=None) -> float:
        """Calcula el costo en tres variantes (sobrecarga con parámetros opcionales).

        * ``calcular_costo(d)``                  -> costo base
        * ``calcular_costo(d, 0.19)``            -> costo base + IVA 19 %
        * ``calcular_costo(d, 0.19, 10)``        -> con IVA y 10 % de descuento
        * ``calcular_costo(d, 0.19, "VIP20")``   -> con IVA y código promocional
        """
        self.validar_parametros(duracion)
        if not 0 <= impuesto <= 1:
            raise CalculoInconsistenteError(f"Impuesto fuera de rango (0-1): {impuesto}")
        subtotal = self.calcular_costo_base(duracion)
        subtotal = self._aplicar_descuento(descuento, subtotal)  # sobrecarga por tipo
        total = round(subtotal * (1 + impuesto), 2)
        if total <= 0:
            raise CalculoInconsistenteError(f"El costo calculado es inconsistente: {total}")
        return total

    @singledispatchmethod
    def _aplicar_descuento(self, descuento, subtotal: float) -> float:
        """Variante por defecto: tipo de descuento no soportado."""
        raise CalculoInconsistenteError(f"Tipo de descuento no soportado: {type(descuento).__name__}")

    @_aplicar_descuento.register(type(None))
    def _(self, descuento, subtotal: float) -> float:
        return subtotal  # sin descuento

    @_aplicar_descuento.register(int)
    @_aplicar_descuento.register(float)
    def _(self, descuento, subtotal: float) -> float:
        if not 0 <= descuento < 100:
            raise CalculoInconsistenteError(f"Porcentaje de descuento inválido: {descuento}%")
        return subtotal * (1 - descuento / 100)

    @_aplicar_descuento.register(str)
    def _(self, descuento, subtotal: float) -> float:
        porcentaje = CODIGOS_PROMO.get(descuento.upper())
        if porcentaje is None:
            raise CalculoInconsistenteError(f"Código promocional inexistente: '{descuento}'")
        return subtotal * (1 - porcentaje / 100)


class ReservaSala(Servicio):
    """Reserva de salas por horas, con capacidad máxima de asistentes."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible: bool = True) -> None:
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}.")
        self._capacidad = capacidad
        self._asignar_id()

    def validar_parametros(self, duracion) -> None:
        if not isinstance(duracion, (int, float)) or not 1 <= duracion <= 8:
            raise ServicioInvalidoError("La sala se reserva entre 1 y 8 horas.")

    def calcular_costo_base(self, duracion) -> float:
        return self.tarifa * duracion

    def describir(self) -> str:
        estado = "disponible" if self.disponible else "NO disponible"
        return (f"Sala '{self.nombre}' (cap. {self._capacidad}) - "
                f"${self.tarifa:,.0f}/hora - {estado}")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos por días, con depósito fijo."""

    DEPOSITO = 50_000.0  # costo fijo de garantía

    def __init__(self, nombre, tarifa_dia, tipo_equipo, disponible: bool = True) -> None:
        super().__init__(nombre, tarifa_dia, disponible)
        if tipo_equipo is None or str(tipo_equipo).strip() == "":
            raise ParametroFaltanteError("Debe indicar el tipo de equipo.")
        self._tipo_equipo = str(tipo_equipo).strip()
        self._asignar_id()

    def validar_parametros(self, duracion) -> None:
        if not isinstance(duracion, int) or isinstance(duracion, bool) or not 1 <= duracion <= 30:
            raise ServicioInvalidoError("El equipo se alquila entre 1 y 30 días (enteros).")

    def calcular_costo_base(self, duracion) -> float:
        return self.tarifa * duracion + self.DEPOSITO

    def describir(self) -> str:
        estado = "disponible" if self.disponible else "NO disponible"
        return (f"Equipo '{self.nombre}' ({self._tipo_equipo}) - "
                f"${self.tarifa:,.0f}/día + depósito - {estado}")


class AsesoriaEspecializada(Servicio):
    """Asesoría por horas; el nivel del asesor modifica la tarifa."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, especialidad, nivel, disponible: bool = True) -> None:
        super().__init__(nombre, tarifa_hora, disponible)
        if especialidad is None or str(especialidad).strip() == "":
            raise ParametroFaltanteError("Debe indicar la especialidad.")
        if str(nivel).lower() not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel inválido '{nivel}'. Use: {', '.join(self.NIVELES)}.")
        self._especialidad = str(especialidad).strip()
        self._nivel = str(nivel).lower()
        self._asignar_id()

    def validar_parametros(self, duracion) -> None:
        if not isinstance(duracion, (int, float)) or not 0.5 <= duracion <= 6 or (duracion * 2) % 1 != 0:
            raise ServicioInvalidoError("La asesoría dura entre 0.5 y 6 horas, en pasos de 0.5.")

    def calcular_costo_base(self, duracion) -> float:
        return self.tarifa * self.NIVELES[self._nivel] * duracion

    def describir(self) -> str:
        estado = "disponible" if self.disponible else "NO disponible"
        return (f"Asesoría '{self.nombre}' ({self._especialidad}, {self._nivel}) - "
                f"${self.tarifa:,.0f}/hora base - {estado}")
