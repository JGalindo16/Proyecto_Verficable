from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST
from openpyxl import Workbook
from io import BytesIO

# Queries externas
from app.sql_queries.generar_horario_queries import (
    GET_SECCIONES_CON_DATOS,
    GET_SALAS_DISPONIBLES
)

class GenerarHorarioService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

        self.dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        self.modulos_por_dia = [
            (9, 0), (10, 0), (11, 0), (12, 0),
            (14, 0), (15, 0), (16, 0), (17, 0)
        ]

    def generar(self):
        try:
            self.cursor.execute(GET_SECCIONES_CON_DATOS)
            secciones = self.cursor.fetchall()

            self.cursor.execute(GET_SALAS_DISPONIBLES)
            salas = self.cursor.fetchall()

            if not secciones or not salas:
                return False, "No hay secciones o salas disponibles para generar el horario."

            disponibilidad = {}
            for dia in self.dias:
                for hora_inicio in self.modulos_por_dia:
                    for sala in salas:
                        key = (sala["classroom_id"], dia, hora_inicio)
                        disponibilidad[key] = None

            asignaciones = []

            for sec in secciones:
                creditos = sec["creditos"]
                inscritos = sec["inscritos"]
                se_asigno = False

                for dia in self.dias:
                    for i in range(len(self.modulos_por_dia) - creditos + 1):
                        bloque = self.modulos_por_dia[i:i + creditos]
                        for sala in salas:
                            if sala["capacity"] < inscritos:
                                continue
                            if all(disponibilidad[(sala["classroom_id"], dia, hora)] is None for hora in bloque):
                                for hora in bloque:
                                    disponibilidad[(sala["classroom_id"], dia, hora)] = sec["section_id"]
                                asignaciones.append({
                                    "curso": sec["curso"],
                                    "seccion": sec["number"],
                                    "profesor": sec["profesor"],
                                    "sala": sala["name"],
                                    "dia": dia,
                                    "hora_inicio": f"{bloque[0][0]:02d}:{bloque[0][1]:02d}",
                                    "hora_fin": f"{bloque[-1][0]+1:02d}:{bloque[-1][1]:02d}"
                                })
                                se_asigno = True
                                break
                        if se_asigno:
                            break
                    if se_asigno:
                        break

                if not se_asigno:
                    return False, f"No fue posible asignar horario a la sección {sec['curso']} - Sec {sec['number']}"

            wb = Workbook()
            ws = wb.active
            ws.title = "Horario generado"
            ws.append(["Curso", "Sección", "Profesor", "Sala", "Día", "Hora inicio", "Hora fin"])
            for a in asignaciones:
                ws.append([a["curso"], a["seccion"], a["profesor"], a["sala"], a["dia"], a["hora_inicio"], a["hora_fin"]])

            output = BytesIO()
            wb.save(output)
            output.seek(0)

            return True, output

        except Exception as e:
            return False, "Error interno al generar el horario."