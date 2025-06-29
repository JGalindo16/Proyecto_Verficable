from app.db import DatabaseConnection
from fpdf import FPDF
from collections import defaultdict
from datetime import datetime
from app.sql_queries import report_queries as q


class CerrarSeccionYReportesService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def _normalizar_nota(self, nota):
        """Normalize grade to be between 1.0 and 7.0."""
        try:
            nota = float(nota)
            if nota < 1.0 or nota > 7.0:
                return 1.0
            return nota
        except (TypeError, ValueError):
            return 1.0

    def _validar_seccion_para_cerrar(self, section_id: int):
        """Query: Validate if section can be closed."""
        self.cursor.execute(q.GET_SECCION_CERRADA, (section_id,))
        row = self.cursor.fetchone()
        
        if not row:
            return False, "La sección especificada no existe."
        if row["closed"]:
            return False, "La sección ya está cerrada."
        
        return True, "Sección válida para cerrar."

    def _obtener_notas_para_cierre(self, section_id: int):
        """Query: Get final grades for section closure."""
        self.cursor.execute(q.GET_FINAL_GRADES_POR_ENROLLMENT, (section_id,))
        notas = self.cursor.fetchall()
        
        notas_procesadas = []
        for row in notas:
            self.cursor.execute(
                q.GET_STUDENT_ID_FROM_ENROLLMENT, (row["enrollment_id"],)
            )
            student = self.cursor.fetchone()
            if student:
                nota = self._normalizar_nota(row["nota_final"])
                notas_procesadas.append({
                    'student_id': student["student_id"],
                    'nota_final': round(nota, 2)
                })
        
        return notas_procesadas

    def _ejecutar_cierre_seccion(self, section_id: int, notas_procesadas: list):
        """Command: Execute section closure with final grades."""
        for nota_data in notas_procesadas:
            self.cursor.execute(
                q.INSERT_NOTA_FINAL,
                (section_id, nota_data['student_id'], nota_data['nota_final'])
            )
        
        self.cursor.execute(q.UPDATE_SECTION_CERRADA, (section_id,))
        self.db.commit()

    def cerrar_seccion(self, section_id: int):
        """Close a section and calculate final grades."""
        try:
            es_valida, mensaje = self._validar_seccion_para_cerrar(section_id)
            if not es_valida:
                return False, mensaje
            
            notas_procesadas = self._obtener_notas_para_cierre(section_id)
            
            self._ejecutar_cierre_seccion(section_id, notas_procesadas)
            
            return (
                True,
                f"Sección {section_id} cerrada exitosamente con "
                f"{len(notas_procesadas)} notas calculadas."
            )
        except Exception as e:
            return False, "Error inesperado al cerrar la sección."

    def generar_reporte_notas_seccion(self, section_id: int):
        """Generate a grades report for a section."""
        try:
            self.cursor.execute(q.GET_REPORTE_POR_EVALUACION, (section_id,))
            rows = self.cursor.fetchall()
            if not rows:
                return None

            data_por_estudiante = defaultdict(lambda: defaultdict(list))
            for row in rows:
                student = row["student_name"]
                eval_id = row["evaluation_id"]
                data_por_estudiante[student][eval_id].append({
                    "type": row["eval_type"],
                    "weight": row["eval_weight"],
                    "instance_name": row["instance_name"],
                    "specific_weight": row["specific_weight"],
                    "score": self._normalizar_nota(row["score"])
                })

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(
                200, 10, txt="Reporte de Notas por Evaluación",
                ln=True, align='C'
            )
            pdf.ln(10)

            for student, evaluaciones in data_por_estudiante.items():
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(200, 10, txt=f"Estudiante: {student}", ln=True)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(70, 8, "Evaluación", border=1)
                pdf.cell(70, 8, "Instancia", border=1)
                pdf.cell(30, 8, "Peso", border=1)
                pdf.cell(20, 8, "Nota", border=1, ln=True)

                for instancias in evaluaciones.values():
                    for instancia in instancias:
                        pdf.set_font("Arial", '', 10)
                        pdf.cell(70, 8, instancia["type"], border=1)
                        pdf.cell(70, 8, instancia["instance_name"], border=1)
                        pdf.cell(
                            30, 8, str(instancia["specific_weight"]), border=1
                        )
                        pdf.cell(
                            20, 8, str(round(instancia["score"], 2)),
                            border=1, ln=True
                        )
                pdf.ln(5)

            path = f"/tmp/reporte_notas_seccion_{section_id}.pdf"
            pdf.output(path)
            return path
        except Exception as e:
            return None

    def generar_reporte_notas_finales(self, section_id: int):
        """Generate a final grades report for a section."""
        try:
            self.cursor.execute(q.GET_REPORTE_NOTAS_FINALES, (section_id,))
            rows = self.cursor.fetchall()
            if not rows:
                return None

            data_por_estudiante = defaultdict(lambda: defaultdict(list))
            for row in rows:
                student = row["student_name"]
                eval_id = row["evaluation_id"]
                data_por_estudiante[student][eval_id].append({
                    "score": self._normalizar_nota(row["score"]),
                    "specific_weight": row["specific_weight"],
                    "eval_weight": row["eval_weight"]
                })

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(
                200, 10, txt="Reporte de Notas Finales",
                ln=True, align='C'
            )
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(100, 10, "Alumno", border=1)
            pdf.cell(40, 10, "Nota Final", border=1, ln=True)

            for student, evaluaciones in data_por_estudiante.items():
                nota_final = 0.0
                for instancias in evaluaciones.values():
                    subtotal = sum(
                        i["score"] * i["specific_weight"] for i in instancias
                    )
                    nota_final += subtotal * instancias[0]["eval_weight"]

                pdf.set_font("Arial", '', 11)
                pdf.cell(100, 10, student, border=1)
                pdf.cell(40, 10, str(round(nota_final, 2)), border=1, ln=True)

            path = f"/tmp/reporte_finales_seccion_{section_id}.pdf"
            pdf.output(path)
            return path
        except Exception as e:
            return None

    def generar_certificado_por_alumno(self, section_id: int, student_id: int):
        """Generate a certificate for a specific student."""
        try:
            self.cursor.execute(
                q.GET_CERTIFICADO_POR_ALUMNO, (section_id, student_id)
            )
            rows = self.cursor.fetchall()
            if not rows:
                return None

            student_name = rows[0]["student_name"]
            course_name = rows[0]["course_name"]
            course_code = rows[0]["code"]
            evaluaciones = defaultdict(
                lambda: {"type": "", "weight": 0.0, "instancias": []}
            )

            for row in rows:
                eval_id = row["evaluation_id"]
                evaluaciones[eval_id]["type"] = row["eval_type"]
                evaluaciones[eval_id]["weight"] = row["eval_weight"]
                evaluaciones[eval_id]["instancias"].append({
                    "name": row["instance_name"],
                    "score": self._normalizar_nota(row["score"]),
                    "specific_weight": row["specific_weight"]
                })

            nota_final = 0.0
            promedios_evaluacion = {}
            for eval_id, data in evaluaciones.items():
                subtotal = sum(
                    inst["score"] * inst["specific_weight"]
                    for inst in data["instancias"]
                )
                promedios_evaluacion[eval_id] = subtotal
                nota_final += subtotal * data["weight"]

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(
                200, 10, txt="Certificado de Notas", ln=True, align='C'
            )
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, txt=f"Estudiante: {student_name}", ln=True)
            pdf.cell(
                200, 10, txt=f"Curso: {course_name} ({course_code})", ln=True
            )
            pdf.cell(
                200, 10, txt=f"Nota Final: {round(nota_final, 2)}", ln=True
            )

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Detalle de Evaluaciones:", ln=True)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(70, 8, "Tipo", border=1)
            pdf.cell(60, 8, "Instancia", border=1)
            pdf.cell(30, 8, "Peso %", border=1)
            pdf.cell(30, 8, "Nota", border=1, ln=True)

            pdf.set_font("Arial", '', 11)
            for data in evaluaciones.values():
                for inst in data["instancias"]:
                    pdf.cell(70, 8, data["type"], border=1)
                    pdf.cell(60, 8, inst["name"], border=1)
                    pdf.cell(
                        30, 8, str(round(inst["specific_weight"], 2)), border=1
                    )
                    pdf.cell(
                        30, 8, str(round(inst["score"], 2)), border=1, ln=True
                    )

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Promedios por Tipo de Evaluación:", ln=True)
            pdf.set_font("Arial", '', 11)
            for eval_id, prom in promedios_evaluacion.items():
                tipo = evaluaciones[eval_id]["type"]
                pdf.cell(
                    200, 8, txt=f"{tipo}: {round(prom, 2)}", ln=True
                )

            path = f"/tmp/certificado_alumno_{student_id}_seccion_{section_id}.pdf"
            pdf.output(path)
            return path
        except Exception as e:
            return None

    def generar_reporte_resumen_por_estudiante(self, student_id: int):
        """Generate an academic summary report for a student."""
        try:
            self.cursor.execute(q.GET_RESUMEN_POR_ESTUDIANTE, (student_id,))
            rows = self.cursor.fetchall()
            if not rows:
                return None

            student_name = rows[0]["student_name"]
            cursos = defaultdict(lambda: {
                "nombre": "",
                "codigo": "",
                "evaluaciones": defaultdict(
                    lambda: {"type": "", "weight": 0.0, "instancias": []}
                )
            })

            for row in rows:
                curso = row["course_name"]
                eval_id = row["evaluation_id"]
                cursos[curso]["nombre"] = curso
                cursos[curso]["codigo"] = row["code"]
                cursos[curso]["evaluaciones"][eval_id]["type"] = row["eval_type"]
                cursos[curso]["evaluaciones"][eval_id]["weight"] = row["eval_weight"]
                cursos[curso]["evaluaciones"][eval_id]["instancias"].append({
                    "name": row["instance_name"],
                    "score": self._normalizar_nota(row["score"]),
                    "specific_weight": row["specific_weight"]
                })

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(
                200, 10, txt="Resumen Académico del Estudiante",
                ln=True, align='C'
            )
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, txt=f"Nombre: {student_name}", ln=True)
            pdf.ln(5)

            promedio_global = 0.0
            cantidad_cursos = 0

            for curso, info in cursos.items():
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(
                    200, 10, txt=f"{info['nombre']} ({info['codigo']})", ln=True
                )

                pdf.set_font("Arial", 'B', 11)
                pdf.cell(70, 8, "Tipo", border=1)
                pdf.cell(60, 8, "Instancia", border=1)
                pdf.cell(30, 8, "Peso %", border=1)
                pdf.cell(30, 8, "Nota", border=1, ln=True)

                nota_final = 0.0
                for eval_data in info["evaluaciones"].values():
                    subtotal = 0.0
                    for inst in eval_data["instancias"]:
                        score = inst["score"]
                        subtotal += score * inst["specific_weight"]
                        pdf.set_font("Arial", '', 11)
                        pdf.cell(70, 8, eval_data["type"], border=1)
                        pdf.cell(60, 8, inst["name"], border=1)
                        pdf.cell(
                            30, 8, str(round(inst["specific_weight"], 2)),
                            border=1
                        )
                        pdf.cell(
                            30, 8, str(round(score, 2)), border=1, ln=True
                        )
                    nota_final += subtotal * eval_data["weight"]

                pdf.cell(
                    200, 8, txt=f"Nota final del curso: {round(nota_final, 2)}",
                    ln=True
                )
                pdf.ln(5)
                promedio_global += nota_final
                cantidad_cursos += 1

            if cantidad_cursos > 0:
                pdf.set_font("Arial", 'B', 12)
                promedio = promedio_global / cantidad_cursos
                pdf.cell(
                    200, 10,
                    txt=f"Promedio General (cursos cerrados): {round(promedio, 2)}",
                    ln=True
                )

            path = f"/tmp/resumen_estudiante_{student_id}.pdf"
            pdf.output(path)
            return path
        except Exception as e:
            return None