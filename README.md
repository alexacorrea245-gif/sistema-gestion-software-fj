# Software FJ – Sistema integral de gestión de clientes, servicios y reservas

Proyecto del curso **Programación (213023)** – UNAD, Fase 4 (Ejercicio 1).
Aplicación en Python **orientada a objetos**, **sin bases de datos**: toda la información
vive en objetos y listas internas; los archivos se usan únicamente para el log de eventos y errores.

## Ejecución
```bash
python main.py        # requiere Python 3.10 o superior; no usa librerías externas
```
Se simulan 18 operaciones (válidas e inválidas). Los eventos y errores quedan en `logs/software_fj.log`.

## Estructura
| Archivo | Contenido |
|---|---|
| `software_fj/excepciones.py` | Excepciones personalizadas (jerarquía `SoftwareFJError`) |
| `software_fj/entidades.py` | Clase abstracta `EntidadBase` |
| `software_fj/cliente.py` | `Cliente` con validaciones y datos encapsulados |
| `software_fj/servicios.py` | `Servicio` (abstracta), `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| `software_fj/reserva.py` | `Reserva`: confirmar, cancelar y procesar |
| `software_fj/gestor.py` | `GestorSistema`: listas internas y ejecución protegida |
| `software_fj/registro.py` | Configuración del archivo de logs |
| `main.py` | Simulación de las operaciones |

## Conceptos aplicados
* **Abstracción:** `EntidadBase` y `Servicio` son clases abstractas (`ABC`, `@abstractmethod`).
* **Herencia y polimorfismo:** tres servicios sobrescriben `validar_parametros`, `calcular_costo_base` y `describir`.
* **Encapsulación:** atributos privados con propiedades y validación en los *setters*.
* **Sobrecarga:** `calcular_costo(duracion, impuesto=0.0, descuento=None)` con parámetros opcionales y
  `functools.singledispatchmethod` para el descuento según su tipo (`None`, número o código promocional).
* **Excepciones:** personalizadas, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento (`raise ... from ...`).
* **Estabilidad:** `GestorSistema._ejecutar` captura errores controlados e inesperados; el programa nunca se detiene.
