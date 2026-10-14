"""
==========================================================
 MÓDULO DE MODELO Y REGISTRO  -  Responsable: Cristhian Giancarlo De la Cruz Saravia
 Contiene: excepciones propias, Validador, jerarquía Persona -> Colaborador,
 patrón Factory Method, clase Asistencia y el registro de colaboradores
 y asistencias (HU01, HU02).
==========================================================
"""

from abc import ABC, abstractmethod
from datetime import datetime

from calculos import (PoliticaHorasExtra, PoliticaExcesoSemanal, LIMITE_HORAS_SEMANALES,
                      LIMITE_HORAS_PRACTICANTE)

FORMATO_FECHA = "%d/%m/%Y"
FORMATO_HORA = "%H:%M"


# ==========================================================
# EXCEPCIONES PROPIAS
# ==========================================================

class AsistenciaError(Exception):
    """Excepción base del sistema."""


class DatoInvalidoError(AsistenciaError):
    """Dato ingresado vacío o con formato incorrecto."""


class ColaboradorNoEncontradoError(AsistenciaError):
    """El código de colaborador no existe."""


class ColaboradorDuplicadoError(AsistenciaError):
    """Ya existe un colaborador con ese código."""


class RegistroNoEncontradoError(AsistenciaError):
    """No existe un registro de asistencia para ese código y fecha."""


# ==========================================================
# VALIDADOR
# ==========================================================
class Validador:
    @staticmethod
    def texto(valor, campo: str) -> str:
        if valor is None or str(valor).strip() == "":
            raise DatoInvalidoError(f"El campo '{campo}' es obligatorio.")
        return str(valor).strip()

    @staticmethod
    def fecha(valor: str) -> str:
        """Valida dd/mm/aaaa y devuelve la fecha normalizada (ej. 1/2/2026 -> 01/02/2026)."""
        try:
            return datetime.strptime(str(valor).strip(), FORMATO_FECHA).strftime(FORMATO_FECHA)
        except ValueError:
            raise DatoInvalidoError("Formato de fecha inválido. Use dd/mm/aaaa.")

    @staticmethod
    def hora(valor: str) -> str:
        """Valida hh:mm (24 h) y devuelve la hora normalizada (ej. 9:5 -> 09:05)."""
        try:
            return datetime.strptime(str(valor).strip(), FORMATO_HORA).strftime(FORMATO_HORA)
        except ValueError:
            raise DatoInvalidoError("Formato de hora inválido. Use hh:mm (24 h).")


# ==========================================================
# HERENCIA: Persona -> Colaborador -> tipos concretos
# ==========================================================
class Persona(ABC):
    def __init__(self, codigo: str, nombres: str):
        self.codigo = Validador.texto(codigo, "código")
        self.nombres = Validador.texto(nombres, "nombres y apellidos")

    @abstractmethod
    def descripcion(self) -> str:
        ...

    def __str__(self):
        return self.descripcion()


class Colaborador(Persona, ABC):
    """Colaborador en home office. Compone (tiene-un) una PoliticaHorasExtra."""

    def __init__(self, codigo: str, nombres: str, area: str, aprobador: str,
                 politica: PoliticaHorasExtra):
        super().__init__(codigo, nombres)
        self.area = Validador.texto(area, "área")
        self.aprobador = Validador.texto(aprobador, "aprobador")
        self._politica = politica

    @abstractmethod
    def tipo(self) -> str:
        ...

    def limite_semanal(self) -> float:
        return self._politica.limite()

    def horas_extra(self, horas_totales: float) -> float:
        return self._politica.calcular(horas_totales)   # delega en la estrategia

    def descripcion(self) -> str:
        return (f"[{self.codigo}] {self.nombres} - Tipo: {self.tipo()} - "
                f"Área: {self.area} - Aprobador: {self.aprobador}")


class ColaboradorHomeOffice(Colaborador):
    def __init__(self, codigo, nombres, area, aprobador):
        super().__init__(codigo, nombres, area, aprobador,
                         PoliticaExcesoSemanal(LIMITE_HORAS_SEMANALES))

    def tipo(self) -> str:
        return "Home office"


class ColaboradorPracticante(Colaborador):
    def __init__(self, codigo, nombres, area, aprobador):
        super().__init__(codigo, nombres, area, aprobador,
                         PoliticaExcesoSemanal(LIMITE_HORAS_PRACTICANTE))

    def tipo(self) -> str:
        return "Practicante"


# ==========================================================
# PATRÓN FACTORY METHOD: creación de colaboradores
# ==========================================================
class FabricaColaborador(ABC):
    @abstractmethod
    def crear_colaborador(self, codigo, nombres, area, aprobador) -> Colaborador:
        ...


class FabricaHomeOffice(FabricaColaborador):
    def crear_colaborador(self, codigo, nombres, area, aprobador) -> Colaborador:
        return ColaboradorHomeOffice(codigo, nombres, area, aprobador)


class FabricaPracticante(FabricaColaborador):
    def crear_colaborador(self, codigo, nombres, area, aprobador) -> Colaborador:
        return ColaboradorPracticante(codigo, nombres, area, aprobador)
FABRICAS = {"1": FabricaHomeOffice(), "2": FabricaPracticante()}


# ==========================================================
# CLASE Asistencia
# ==========================================================
class Asistencia:
    def __init__(self, codigo_usuario: str, fecha: str, hora_inicio: str, hora_fin: str):
        self.codigo_usuario = Validador.texto(codigo_usuario, "código")
        self.fecha = Validador.fecha(fecha)
        self.hora_inicio = Validador.hora(hora_inicio)
        self.hora_fin = Validador.hora(hora_fin)
        if self.hora_inicio == self.hora_fin:
            raise DatoInvalidoError("La hora de inicio y la hora de fin no pueden ser iguales.")

    def horas_trabajadas(self) -> float:
        """Horas de la jornada (soporta turnos que cruzan la medianoche)."""
        inicio = datetime.strptime(self.hora_inicio, FORMATO_HORA)
        fin = datetime.strptime(self.hora_fin, FORMATO_HORA)
        diferencia = (fin - inicio).total_seconds() / 3600
        if diferencia < 0:
            diferencia += 24
        return round(diferencia, 2)

    def __str__(self):
        return (f"{self.codigo_usuario:<8} {self.fecha:<12} "
                f"{self.hora_inicio:<8} {self.hora_fin:<8} "
                f"{self.horas_trabajadas():>6.2f} h")


# ==========================================================
# REGISTRO (HU01, HU02). Se integra a GestionAsistencia como mixin
# ==========================================================

class RegistroMixin:
    """Registro de colaboradores y de asistencias."""

    def registrarColaborador(self, codigo, nombres, area, aprobador, tipo="1") -> Colaborador:
        codigo = Validador.texto(codigo, "código")
        if self.buscarColaboradorPorCodigo(codigo):
            raise ColaboradorDuplicadoError("Ya existe un colaborador con ese código.")
        fabrica = FABRICAS.get(str(tipo).strip())
        if fabrica is None:
            raise DatoInvalidoError("Tipo de colaborador inválido (1 = Home office, 2 = Practicante).")
        nuevo = fabrica.crear_colaborador(codigo, nombres, area, aprobador)
        self.listaColaboradores.append(nuevo)
        self._notificar("COLABORADOR_REGISTRADO", {"codigo": nuevo.codigo})
        return nuevo

    def registrarAsistencia(self, codigo, fecha, hora_inicio, hora_fin) -> Asistencia:
        colaborador = self.buscarColaboradorPorCodigo(codigo)
        if colaborador is None:
            raise ColaboradorNoEncontradoError(
                "El colaborador no existe. Regístrelo primero (opción 1).")
        nueva = Asistencia(colaborador.codigo, fecha, hora_inicio, hora_fin)
        self.listaAsistencias.append(nueva)
        total = self._horas_totales(colaborador.codigo)
        self._notificar("ASISTENCIA_REGISTRADA", {
            "codigo": colaborador.codigo, "colaborador": colaborador,
            "horas_totales": total, "horas_extra": colaborador.horas_extra(total)})
        return nueva# Proyecto_asistencia


