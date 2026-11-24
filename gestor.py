"""Gestor central: administra listas internas de clientes, servicios y reservas."""
from .cliente import Cliente
from .excepciones import ClienteInvalidoError, SoftwareFJError
from .registro import obtener_logger
from .reserva import Reserva

log = obtener_logger()


class GestorSistema:
    """Coordina las operaciones y garantiza que ningún error detenga el programa."""

    def __init__(self) -> None:
        self._clientes: list[Cliente] = []
        self._servicios: list = []
        self._reservas: list[Reserva] = []

    @property
    def clientes(self):
        return tuple(self._clientes)  # copia inmutable: protege la lista interna

    @property
    def servicios(self):
        return tuple(self._servicios)

    @property
    def reservas(self):
        return tuple(self._reservas)

    def _ejecutar(self, descripcion: str, funcion, *args, **kwargs):
        """Ejecuta una operación capturando y registrando cualquier error."""
        try:
            resultado = funcion(*args, **kwargs)
        except SoftwareFJError as error:
            # Error controlado del dominio; se muestra la causa si fue encadenado
            causa = f" (causa: {error.__cause__})" if error.__cause__ else ""
            log.error("%s -> %s: %s%s", descripcion, type(error).__name__, error, causa)
            print(f"   [ERROR CONTROLADO] {type(error).__name__}: {error}{causa}")
            return None
        except Exception as error:  # error inesperado: el sistema sigue vivo
            log.critical("%s -> ERROR INESPERADO %s: %s", descripcion, type(error).__name__, error)
            print(f"   [ERROR INESPERADO] {type(error).__name__}: {error}")
            return None
        else:
            log.info("%s -> OK", descripcion)
            return resultado
        finally:
            log.info("Operación finalizada: %s", descripcion)

    # ------------------- operaciones -------------------
    def registrar_cliente(self, nombre, documento, correo, telefono):
        def _registrar():
            if any(c.documento == str(documento).strip() for c in self._clientes):
                raise ClienteInvalidoError(f"Ya existe un cliente con documento {documento}.")
            cliente = Cliente(nombre, documento, correo, telefono)
            self._clientes.append(cliente)
            return cliente
        return self._ejecutar("Registrar cliente", _registrar)

    def crear_servicio(self, clase, *args, **kwargs):
        def _crear():
            servicio = clase(*args, **kwargs)
            self._servicios.append(servicio)
            return servicio
        return self._ejecutar(f"Crear servicio {clase.__name__}", _crear)

    def crear_reserva(self, cliente, servicio, duracion):
        def _crear():
            reserva = Reserva(cliente, servicio, duracion)
            self._reservas.append(reserva)
            return reserva
        return self._ejecutar("Crear reserva", _crear)

    def ejecutar(self, descripcion: str, funcion, *args, **kwargs):
        """Permite ejecutar cualquier operación externa de forma protegida."""
        return self._ejecutar(descripcion, funcion, *args, **kwargs)
