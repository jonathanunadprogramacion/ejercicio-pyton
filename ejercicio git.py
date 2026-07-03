import datetime
import logging
import abc
from typing import List, Optional

# Configuración de logging
logging.basicConfig(
    filename='eventos.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Excepciones personalizadas
class ErrorSistema(Exception):
    """Excepción base para el sistema."""
    pass

class DatosInvalidosError(ErrorSistema):
    """Error por datos inválidos."""
    pass

class ServicioNoDisponibleError(ErrorSistema):
    """Error cuando un servicio no está disponible."""
    pass

class ReservaInvalidaError(ErrorSistema):
    """Error en operaciones de reserva."""
    pass

# Clase Abstracta base
class EntidadBase(abc.ABC):
    """Clase abstracta que representa entidades generales."""
    
    def __init__(self, id_entidad: str):
        if not id_entidad or not isinstance(id_entidad, str):
            raise DatosInvalidosError("ID de entidad debe ser una cadena no vacía")
        self._id = id_entidad
    
    @property
    def id(self) -> str:
        return self._id
    
    @abc.abstractmethod
    def obtener_info(self) -> str:
        pass
