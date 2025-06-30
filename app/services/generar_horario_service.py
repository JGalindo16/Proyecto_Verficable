from app.db import DatabaseConnection
from openpyxl import Workbook
from io import BytesIO

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

    def _get_sections_and_classrooms(self):
        self.cursor.execute(GET_SECCIONES_CON_DATOS)
        secciones = self.cursor.fetchall()

        self.cursor.execute(GET_SALAS_DISPONIBLES)
        salas = self.cursor.fetchall()

        return secciones, salas

    def _validate_data_availability(self, secciones, salas):
        if not secciones or not salas:
            return (
                False, 
                "No hay secciones o salas disponibles para generar el "
                "horario."
            )
        return True, None

    def _initialize_availability_matrix(self, salas):
        disponibilidad = {}
        for dia in self.dias:
            for hora_inicio in self.modulos_por_dia:
                for sala in salas:
                    key = (sala["classroom_id"], dia, hora_inicio)
                    disponibilidad[key] = None
        return disponibilidad

    def _check_classroom_capacity(self, sala, inscritos):
        return sala["capacity"] >= inscritos

    def _check_time_slots_available(self, disponibilidad, sala, dia, bloque):
        return all(
            disponibilidad[(sala["classroom_id"], dia, hora)] is None 
            for hora in bloque
        )

    def _mark_time_slots_occupied(self, disponibilidad, sala, dia, bloque, 
                                 section_id):
        for hora in bloque:
            disponibilidad[(sala["classroom_id"], dia, hora)] = section_id

    def _create_assignment_record(self, sec, sala, dia, bloque):
        return {
            "curso": sec["curso"],
            "seccion": sec["number"],
            "profesor": sec["profesor"],
            "sala": sala["name"],
            "dia": dia,
            "hora_inicio": f"{bloque[0][0]:02d}:{bloque[0][1]:02d}",
            "hora_fin": f"{bloque[-1][0]+1:02d}:{bloque[-1][1]:02d}"
        }

    def _try_assign_section_to_slot(self, sec, dia, bloque, salas, 
                                   disponibilidad, asignaciones):
        for sala in salas:
            if not self._check_classroom_capacity(sala, sec["inscritos"]):
                continue
            
            if self._check_time_slots_available(
                disponibilidad, sala, dia, bloque
            ):
                self._mark_time_slots_occupied(
                    disponibilidad, sala, dia, bloque, sec["section_id"]
                )
                
                assignment = self._create_assignment_record(sec, sala, dia, bloque)
                asignaciones.append(assignment)
                
                return True
        
        return False

    def _assign_section_schedule(self, sec, salas, disponibilidad, 
                                asignaciones):
        creditos = sec["creditos"]
        
        for dia in self.dias:
            for i in range(len(self.modulos_por_dia) - creditos + 1):
                bloque = self.modulos_por_dia[i:i + creditos]
                
                if self._try_assign_section_to_slot(
                    sec, dia, bloque, salas, disponibilidad, asignaciones
                ):
                    return True
        
        return False

    def _process_all_sections(self, secciones, salas, disponibilidad):
        asignaciones = []
        
        for sec in secciones:
            if not self._assign_section_schedule(
                sec, salas, disponibilidad, asignaciones
            ):
                return (
                    False, 
                    f"No fue posible asignar horario a la sección "
                    f"{sec['curso']} - Sec {sec['number']}",
                    None
                )
        
        return True, None, asignaciones

    def _create_excel_workbook(self, asignaciones):
        wb = Workbook()
        ws = wb.active
        ws.title = "Horario generado"
        
        ws.append([
            "Curso", "Sección", "Profesor", "Sala", 
            "Día", "Hora inicio", "Hora fin"
        ])
        
        for assignment in asignaciones:
            ws.append([
                assignment["curso"], assignment["seccion"], 
                assignment["profesor"], assignment["sala"], 
                assignment["dia"], assignment["hora_inicio"], 
                assignment["hora_fin"]
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output

    def generar(self):
        try:
            secciones, salas = self._get_sections_and_classrooms()
            is_valid, error_msg = self._validate_data_availability(
                secciones, salas
            )
            if not is_valid:
                return False, error_msg
            
            disponibilidad = self._initialize_availability_matrix(salas)
            success, error_msg, asignaciones = self._process_all_sections(
                secciones, salas, disponibilidad
            )
            if not success:
                return False, error_msg
            output = self._create_excel_workbook(asignaciones)
            
            return True, output

        except Exception:
            return False, "Error interno al generar el horario."