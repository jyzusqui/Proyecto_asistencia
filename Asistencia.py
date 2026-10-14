"""
==========================================================
 SISTEMA DE REGISTRO Y CONTROL DE ASISTENCIA HOME OFFICE

 Empresa: Tottus - Área de Gestión de Procesos
 Curso: IS275 - Fundamentos de Programación 2

 Grupo 7:
   - Cristhian Giancarlo De la Cruz Saravia
   - Juan José Yzusqui Calderón
   - Omar Alejandro Laime Ccaccro
==========================================================
"""

from datetime import datetime


FORMATO_FECHA = "%d/%m/%Y"
FORMATO_HORA = "%H:%M"
LIMITE_HORAS_SEMANALES = 48


# ==========================================================
# PARTE 1
# INTEGRANTE: CRISTHIAN GIANCARLO DE LA CRUZ SARAVIA
# ROL: MODELO Y CREACIÓN DE OBJETOS
# ==========================================================


# ==========================================================
# CLASE: Colaborador
# ==========================================================

class Colaborador:

    def __init__(self, codigo: str, nombres: str, area: str, aprobador: str):
        self.codigo = codigo
        self.nombres = nombres
        self.area = area
        self.aprobador = aprobador

    def __str__(self):
        return (
            f"[{self.codigo}] {self.nombres} - "
            f"Área: {self.area} - "
            f"Aprobador: {self.aprobador}"
        )


# ==========================================================
# CLASE: Asistencia
# ==========================================================

class Asistencia:

    def __init__(
        self,
        codigo_usuario: str,
        fecha: str,
        hora_inicio: str,
        hora_fin: str
    ):
        self.codigo_usuario = codigo_usuario
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

    def horas_trabajadas(self) -> float:
        """
        Calcula las horas trabajadas en un registro diario.
        """

        try:
            inicio = datetime.strptime(
                self.hora_inicio,
                FORMATO_HORA
            )

            fin = datetime.strptime(
                self.hora_fin,
                FORMATO_HORA
            )

            diferencia = (
                fin - inicio
            ).total_seconds() / 3600

            # En caso el turno cruce la medianoche
            if diferencia < 0:
                diferencia += 24

            return round(diferencia, 2)

        except ValueError:
            return 0.0

    def __str__(self):

        return (
            f"{self.codigo_usuario:<8} "
            f"{self.fecha:<12} "
            f"{self.hora_inicio:<8} "
            f"{self.hora_fin:<8} "
            f"{self.horas_trabajadas():>6.2f} h"
        )


# ==========================================================
# CLASE PRINCIPAL: GestionAsistencia
# ==========================================================

class GestionAsistencia:

    def __init__(self):

        self.listaColaboradores = []
        self.listaAsistencias = []


    # ======================================================
    # VALIDACIONES
    # ======================================================

    def _validar_texto(self, valor: str) -> bool:

        return (
            valor is not None
            and valor.strip() != ""
        )


    def _validar_fecha(self, valor: str) -> bool:

        try:

            datetime.strptime(
                valor,
                FORMATO_FECHA
            )

            return True

        except ValueError:

            return False


    def _validar_hora(self, valor: str) -> bool:

        try:

            datetime.strptime(
                valor,
                FORMATO_HORA
            )

            return True

        except ValueError:

            return False


    # ======================================================
    # BÚSQUEDAS AUXILIARES
    # ======================================================

    def buscarColaboradorPorCodigo(
        self,
        codigo: str
    ):

        for colaborador in self.listaColaboradores:

            if colaborador.codigo == codigo:

                return colaborador

        return None


    def buscarAsistenciasPorCodigo(
        self,
        codigo: str
    ):

        return [
            asistencia
            for asistencia in self.listaAsistencias
            if asistencia.codigo_usuario == codigo
        ]


    # ======================================================
    # HU01: REGISTRAR COLABORADOR
    # ======================================================

    def registrarColaborador(self):

        print(
            "\n------ REGISTRAR COLABORADOR ------"
        )

        codigo = input(
            "Ingrese código de usuario: "
        ).strip()


        if self.buscarColaboradorPorCodigo(codigo):

            print(
                "Error: ya existe un colaborador "
                "con ese código."
            )

            return


        nombres = input(
            "Ingrese nombres y apellidos: "
        ).strip()

        area = input(
            "Ingrese área: "
        ).strip()

        aprobador = input(
            "Ingrese aprobador (jefe directo): "
        ).strip()


        if not (
            self._validar_texto(codigo)
            and self._validar_texto(nombres)
            and self._validar_texto(area)
            and self._validar_texto(aprobador)
        ):

            print(
                "Error: todos los campos "
                "son obligatorios."
            )

            return


        nuevo = Colaborador(
            codigo,
            nombres,
            area,
            aprobador
        )

        self.listaColaboradores.append(nuevo)


        print(
            "------------------------------------"
        )

        print(
            "Colaborador registrado exitosamente."
        )


    # ======================================================
    # HU02: REGISTRAR ASISTENCIA DIARIA
    # ======================================================

    def registrarAsistencia(self):

        print(
            "\n------ REGISTRAR ASISTENCIA ------"
        )

        codigo = input(
            "Ingrese código de usuario: "
        ).strip()


        colaborador = (
            self.buscarColaboradorPorCodigo(codigo)
        )


        if not colaborador:

            print(
                "Error: el colaborador no existe. "
                "Regístrelo primero (opción 1)."
            )

            return


        fecha = input(
            "Ingrese fecha (dd/mm/aaaa): "
        ).strip()


        if not self._validar_fecha(fecha):

            print(
                "Error: formato de fecha inválido. "
                "Use dd/mm/aaaa."
            )

            return


        hora_inicio = input(
            "Ingrese hora de inicio (hh:mm): "
        ).strip()


        if not self._validar_hora(hora_inicio):

            print(
                "Error: formato de hora inválido. "
                "Use hh:mm (24h)."
            )

            return


        hora_fin = input(
            "Ingrese hora de fin (hh:mm): "
        ).strip()


        if not self._validar_hora(hora_fin):

            print(
                "Error: formato de hora inválido. "
                "Use hh:mm (24h)."
            )

            return


        nueva = Asistencia(
            codigo,
            fecha,
            hora_inicio,
            hora_fin
        )

        self.listaAsistencias.append(nueva)


        print(
            "------------------------------------"
        )

        print(
            "Asistencia registrada correctamente."
        )
