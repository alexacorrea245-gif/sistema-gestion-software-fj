"""Excepciones personalizadas del sistema Software FJ.

Todas heredan de ``SoftwareFJError`` para poder capturarlas de forma
conjunta cuando se necesite, o de forma individual cuando se requiera
un tratamiento específico.
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema."""


class ParametroFaltanteError(SoftwareFJError):
    """Se omitió un parámetro obligatorio (None o cadena vacía)."""


class ClienteInvalidoError(SoftwareFJError):
    """Los datos de un cliente no cumplen las validaciones."""


class ServicioInvalidoError(SoftwareFJError):
    """Los parámetros de un servicio no son válidos."""


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio solicitado no está disponible para reservar."""


class ReservaInvalidaError(SoftwareFJError):
    """La reserva no pudo crearse por datos o condiciones incorrectas."""


class OperacionNoPermitidaError(SoftwareFJError):
    """La operación no es válida para el estado actual del objeto."""


class CalculoInconsistenteError(SoftwareFJError):
    """Un cálculo de costos produjo un resultado inconsistente."""
