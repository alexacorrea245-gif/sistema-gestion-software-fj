"""Clase Reserva: integra cliente, servicio, duración y estado."""
from enum import Enum

from .cliente import Cliente
from .entidades import EntidadBase
from .excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from .registro import obtener_logger
from .servicios import Servicio

log = obtener_logger()


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    PROCESADA = "Procesada"
    CANCELADA = "Cancelada"


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    IVA = 0.19  # impuesto aplicado al procesar
    _CATEGORIA = "RES"

    def __init__(self, cliente, servicio, duracion) -> None:
        super().__init__()
        # Validación de tipos: evita objetos nulos o incorrectos
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible.")
        try:
            servicio.validar_parametros(duracion)  # cada servicio valida a su manera
        except ServicioInvalidoError as error:
            # Encadenamiento de excepciones: conserva la causa original
            raise ReservaInvalidaError(
                f"Duración {duracion!r} no válida para '{servicio.nombre}'."
            ) from error
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = EstadoReserva.PENDIENTE
        self._total = None
        self._asignar_id()

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def total(self):
        return self._total

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    def confirmar(self) -> bool:
        """Confirma la reserva (try / except / else / finally)."""
        try:
            if self._estado is not EstadoReserva.PENDIENTE:
                raise OperacionNoPermitidaError(
                    f"No se puede confirmar una reserva en estado {self._estado.value}."
                )
            if not self._servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self._servicio.nombre}' dejó de estar disponible."
                )
        except (OperacionNoPermitidaError, ServicioNoDisponibleError) as error:
            # Encadenamiento: el error de bajo nivel queda como causa (__cause__)
            raise ReservaInvalidaError(f"No se pudo confirmar la reserva #{self.id}.") from error
        else:  # solo se ejecuta si el bloque try no lanzó excepciones
            self._estado = EstadoReserva.CONFIRMADA
            log.info("Reserva #%s confirmada.", self.id)
            return True
        finally:  # se ejecuta siempre, haya o no error
            log.info("Intento de confirmación de reserva #%s finalizado.", self.id)

    def cancelar(self) -> bool:
        """Cancela la reserva si aún no fue procesada ni cancelada."""
        try:
            if self._estado in (EstadoReserva.PROCESADA, EstadoReserva.CANCELADA):
                raise OperacionNoPermitidaError(
                    f"No se puede cancelar una reserva {self._estado.value.lower()}."
                )
        except OperacionNoPermitidaError as error:
            raise ReservaInvalidaError(f"No se pudo cancelar la reserva #{self.id}.") from error
        else:
            self._estado = EstadoReserva.CANCELADA
            log.info("Reserva #%s cancelada.", self.id)
            return True
        finally:
            log.info("Intento de cancelación de reserva #%s finalizado.", self.id)

    def procesar(self, descuento=None) -> float:
        """Calcula el total (con IVA y descuento opcional) y cierra la reserva."""
        try:
            if self._estado is not EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError("Solo se procesan reservas confirmadas.")
            total = self._servicio.calcular_costo(self._duracion, self.IVA, descuento)
        except (OperacionNoPermitidaError, CalculoInconsistenteError, ServicioInvalidoError) as error:
            raise ReservaInvalidaError(f"No se pudo procesar la reserva #{self.id}.") from error
        else:
            self._total = total
            self._estado = EstadoReserva.PROCESADA
            log.info("Reserva #%s procesada. Total: $%s", self.id, f"{total:,.2f}")
            return total
        finally:
            log.info("Fin del procesamiento de reserva #%s.", self.id)

    def describir(self) -> str:
        total = f" | Total: ${self._total:,.2f}" if self._total is not None else ""
        return (f"Reserva #{self.id} [{self._estado.value}] {self._cliente.nombre} -> "
                f"{self._servicio.nombre} x {self._duracion}{total}")
