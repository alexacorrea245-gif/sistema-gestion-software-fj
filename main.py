"""Simulación de 15 operaciones de Software FJ (sin bases de datos).

Ejecutar:  python main.py
Los errores y eventos quedan registrados en logs/software_fj.log
"""
from software_fj.gestor import GestorSistema
from software_fj.registro import ARCHIVO_LOG, obtener_logger
from software_fj.servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala

log = obtener_logger()


def titulo(numero: int, texto: str) -> None:
    """Imprime el encabezado de cada operación simulada."""
    print(f"\n[{numero:02d}] {texto}")


def main() -> None:
    log.info("===== INICIO DE LA SIMULACIÓN SOFTWARE FJ =====")
    g = GestorSistema()
    print("=" * 66)
    print("  SOFTWARE FJ - Sistema integral de clientes, servicios y reservas")
    print("=" * 66)

    # ---------- CLIENTES ----------
    titulo(1, "Registro VÁLIDO de cliente")
    ana = g.registrar_cliente("Ana Torres", "1012345678", "ana.torres@correo.com", "3101234567")
    print("  ", ana)

    titulo(2, "Registro INVÁLIDO de cliente (correo mal formado)")
    g.registrar_cliente("Luis Pérez", "79876543", "luis#correo", "3207654321")

    titulo(3, "Registro INVÁLIDO de cliente (teléfono faltante)")
    g.registrar_cliente("Marta Ríos", "52123456", "marta@correo.com", None)

    titulo(4, "Registro VÁLIDO de segundo cliente")
    carlos = g.registrar_cliente("Carlos Gómez", "80123456", "carlos.gomez@correo.com", "3159876543")
    print("  ", carlos)

    titulo(5, "Registro INVÁLIDO (documento duplicado)")
    g.registrar_cliente("Ana Duplicada", "1012345678", "otra@correo.com", "3001112233")

    # ---------- SERVICIOS ----------
    titulo(6, "Creación CORRECTA de los tres tipos de servicio")
    sala = g.crear_servicio(ReservaSala, "Sala Innovación", 80_000, 12)
    equipo = g.crear_servicio(AlquilerEquipo, "Video Beam 4K", 45_000, "Proyector")
    asesoria = g.crear_servicio(AsesoriaEspecializada, "Arquitectura de Software", 120_000, "Software", "senior")
    for s in (sala, equipo, asesoria):
        print("  ", s)

    titulo(7, "Creación INCORRECTA de servicio (capacidad negativa)")
    g.crear_servicio(ReservaSala, "Sala Rota", 70_000, -5)

    titulo(8, "Creación INCORRECTA de servicio (nivel de asesor inexistente)")
    g.crear_servicio(AsesoriaEspecializada, "Bases de Datos", 100_000, "BD", "maestro")

    # ---------- RESERVAS ----------
    titulo(9, "Reserva EXITOSA: confirmar + procesar con IVA y código VIP20")
    r1 = g.crear_reserva(ana, sala, 3)
    g.ejecutar("Confirmar reserva 1", r1.confirmar)
    total = g.ejecutar("Procesar reserva 1", r1.procesar, "VIP20")
    print("  ", r1)

    titulo(10, "Reserva FALLIDA (duración fuera de rango: 12 horas) - excepción encadenada")
    g.crear_reserva(carlos, sala, 12)

    titulo(11, "Reserva FALLIDA (servicio no disponible)")
    equipo.cambiar_disponibilidad(False)
    g.crear_reserva(carlos, equipo, 5)
    equipo.cambiar_disponibilidad(True)

    titulo(12, "Reserva FALLIDA (cliente inexistente / None)")
    g.crear_reserva(None, asesoria, 2)

    titulo(13, "Reserva EXITOSA de equipo y asesoría; cancelación válida")
    r2 = g.crear_reserva(carlos, equipo, 4)
    r3 = g.crear_reserva(carlos, asesoria, 1.5)
    g.ejecutar("Confirmar reserva 3", r3.confirmar)
    g.ejecutar("Cancelar reserva 2 (pendiente)", r2.cancelar)
    print("  ", r2)
    print("  ", r3)

    titulo(14, "Operación NO PERMITIDA: cancelar una reserva ya procesada")
    g.ejecutar("Cancelar reserva 1 (procesada)", r1.cancelar)
    print("   Estado de la reserva 1 se mantiene:", r1.estado.value)

    titulo(15, "Cálculo INCONSISTENTE (descuento 150 %) y código promo inexistente")
    g.ejecutar("Procesar reserva 3 con descuento 150%", r3.procesar, 150)
    g.ejecutar("Procesar reserva 3 con código falso", r3.procesar, "GRATIS")
    print("   Estado de la reserva 3 tras los errores:", r3.estado.value)

    titulo(16, "Sobrecarga de métodos: calcular_costo con distintos parámetros")
    print(f"   Solo base .......... ${sala.calcular_costo(2):>12,.2f}")
    print(f"   Con IVA 19% ........ ${sala.calcular_costo(2, 0.19):>12,.2f}")
    print(f"   IVA + 10% desc. .... ${sala.calcular_costo(2, 0.19, 10):>12,.2f}")
    print(f"   IVA + código PROMO10 ${sala.calcular_costo(2, 0.19, 'PROMO10'):>12,.2f}")

    titulo(17, "ERROR INESPERADO (división entre cero): el sistema continúa")
    g.ejecutar("Promedio de reservas sin datos", lambda: sum([]) / len([]))

    titulo(18, "Procesar correctamente la reserva 3 tras los errores")
    total3 = g.ejecutar("Procesar reserva 3", r3.procesar, "PROMO10")
    print("  ", r3)

    # ---------- RESUMEN ----------
    print("\n" + "=" * 66)
    print(f"  RESUMEN: {len(g.clientes)} clientes | {len(g.servicios)} servicios | {len(g.reservas)} reservas")
    for r in g.reservas:
        print("   -", r)
    print(f"  Registro de eventos y errores en: {ARCHIVO_LOG.name}")
    print("  El programa terminó sin interrupciones.")
    print("=" * 66)
    log.info("===== FIN DE LA SIMULACIÓN =====")


if __name__ == "__main__":
    main()
