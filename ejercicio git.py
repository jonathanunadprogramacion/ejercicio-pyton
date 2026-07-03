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

# Clase Cliente
class Cliente(EntidadBase):
    """Clase para gestión de clientes con encapsulación."""
    
    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        super().__init__(id_cliente)
        self._validar_datos(nombre, email, telefono)
        self._nombre = nombre
        self._email = email
        self._telefono = telefono
        logging.info(f"Cliente creado: {id_cliente} - {nombre}")
    
    def _validar_datos(self, nombre: str, email: str, telefono: str):
        if not nombre or len(nombre.strip()) < 3:
            raise DatosInvalidosError("Nombre debe tener al menos 3 caracteres")
        if not email or "@" not in email:
            raise DatosInvalidosError("Email inválido")
        if not telefono or len(telefono) < 7:
            raise DatosInvalidosError("Teléfono inválido")
    
    @property
    def nombre(self) -> str:
        return self._nombre
    
    @property
    def email(self) -> str:
        return self._email
    
    def obtener_info(self) -> str:
        return f"Cliente {self.id}: {self._nombre} ({self._email})"

# Clase Abstracta Servicio
class Servicio(EntidadBase, abc.ABC):
    """Clase abstracta para servicios."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float):
        super().__init__(id_servicio)
        if not nombre:
            raise DatosInvalidosError("Nombre de servicio requerido")
        if precio_base <= 0:
            raise DatosInvalidosError("Precio base debe ser positivo")
        self._nombre = nombre
        self._precio_base = precio_base
        self._disponible = True
    
    @property
    def nombre(self) -> str:
        return self._nombre
    
    @property
    def precio_base(self) -> float:
        return self._precio_base
    
    @abc.abstractmethod
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """Método polimórfico para calcular costo."""
        pass
    
    def describir(self) -> str:
        return f"Servicio: {self._nombre} - Precio base: ${self._precio_base}"
    
    def obtener_info(self) -> str:
        return self.describir()
    
    def set_disponibilidad(self, disponible: bool):
        self._disponible = disponible

# Servicios especializados (Herencia y Polimorfismo)
class ReservaSala(Servicio):
    """Servicio de reserva de sala."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, capacidad: int):
        super().__init__(id_servicio, nombre, precio_base)
        self.capacidad = capacidad
    
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        if duracion <= 0:
            raise DatosInvalidosError("Duración debe ser positiva")
        costo = self.precio_base * duracion
        if kwargs.get('es_fin_de_semana', False):
            costo *= 1.2
        return round(costo, 2)
    
    def describir(self) -> str:
        return f"{super().describir()} - Capacidad: {self.capacidad} personas"

class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, tipo_equipo: str):
        super().__init__(id_servicio, nombre, precio_base)
        self.tipo_equipo = tipo_equipo
    
    def calcular_costo(self, duracion: float, cantidad: int = 1, **kwargs) -> float:
        if duracion <= 0 or cantidad <= 0:
            raise DatosInvalidosError("Duración y cantidad deben ser positivas")
        costo = self.precio_base * duracion * cantidad
        if kwargs.get('seguro', False):
            costo *= 1.1
        return round(costo, 2)
    
    def describir(self) -> str:
        return f"{super().describir()} - Equipo: {self.tipo_equipo}"

class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, especialidad: str):
        super().__init__(id_servicio, nombre, precio_base)
        self.especialidad = especialidad
    
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        if duracion <= 0:
            raise DatosInvalidosError("Duración debe ser positiva")
        costo = self.precio_base * duracion
        descuento = kwargs.get('descuento', 0)
        if 0 < descuento <= 100:
            costo *= (1 - descuento / 100)
        return round(costo, 2)
    
    def describir(self) -> str:
        return f"{super().describir()} - Especialidad: {self.especialidad}"

# Clase Reserva
class Reserva:
    """Clase para gestionar reservas."""
    
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: float, fecha: datetime.date):
        self._validar_parametros(id_reserva, cliente, servicio, duracion, fecha)
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.fecha = fecha
        self.estado = "Pendiente"
        logging.info(f"Reserva creada: {id_reserva} para cliente {cliente.id}")
    
    def _validar_parametros(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: float, fecha: datetime.date):
        if not id_reserva:
            raise DatosInvalidosError("ID de reserva requerido")
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Cliente y Servicio deben ser instancias válidas")
        if duracion <= 0:
            raise DatosInvalidosError("Duración debe ser positiva")
        if fecha < datetime.date.today():
            raise ReservaInvalidaError("La fecha no puede ser en el pasado")
        if not servicio._disponible:
            raise ServicioNoDisponibleError(f"Servicio {servicio.nombre} no disponible")


