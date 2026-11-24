"""Configuración del archivo de logs (eventos y errores)."""
import logging
from pathlib import Path

# Carpeta y archivo donde se guardan todos los eventos del sistema
RUTA_LOGS = Path(__file__).resolve().parent.parent / "logs"
ARCHIVO_LOG = RUTA_LOGS / "software_fj.log"


def obtener_logger() -> logging.Logger:
    """Devuelve el logger único del sistema, configurándolo una sola vez."""
    logger = logging.getLogger("software_fj")
    if not logger.handlers:  # evita duplicar manejadores si se llama varias veces
        RUTA_LOGS.mkdir(parents=True, exist_ok=True)  # crea la carpeta si no existe
        logger.setLevel(logging.INFO)
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
        manejador.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
        )
        logger.addHandler(manejador)
        logger.propagate = False  # el log solo va al archivo
    return logger
