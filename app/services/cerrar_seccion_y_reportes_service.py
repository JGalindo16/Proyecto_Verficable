from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST
from datetime import datetime
from fpdf import FPDF
import os

class CerrarSeccionYReportesService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def cerrar_seccion(self, section_id: int):
        try:
            self.cursor.execute("SELECT closed FROM sections WHERE section_id = %s", (section_id,))
            row = self.cursor.fetchone()
            if not row:
                return False, "Sección no encontrada."
            if row["closed"]:
                return False, "La sección ya está cerrada."

            self.cursor.execute("""
                SELECT e.enrollment_id, SUM(g.score * ei.specific_weight / 100.0) AS nota_final
                FROM enrollments e
                JOIN grades g ON g.enrollment_id = e.enrollment_id
                JOIN evaluation_instances ei ON ei.instance_eval_id = g.instance_eval_id
                JOIN evaluations ev ON ev.evaluation_id = ei.evaluation_id
                WHERE ev.section_id = %s
                GROUP BY e.enrollment_id
            """, (section_id,))
            notas = self.cursor.fetchall()

            for row in notas:
                self.cursor.execute("SELECT student_id FROM enrollments WHERE enrollment_id = %s", (row["enrollment_id"],))
                student = self.cursor.fetchone()
                if not student:
                    continue
                try:
                    nota = float(row["nota_final"]) if row["nota_final"] is not None else 1.0
                    if nota < 1.0 or nota > 7.0:
                        nota = 1.0
                except (TypeError, ValueError):
                    nota = 1.0

                self.cursor.execute("""
                    INSERT INTO final_grades (section_id, student_id, final_score)
                    VALUES (%s, %s, %s)
                """, (section_id, student["student_id"], round(nota, 2)))

            self.cursor.execute("UPDATE sections SET closed = TRUE WHERE section_id = %s", (section_id,))
            self.db.commit()

            return True, f"Sección {section_id} cerrada exitosamente con {len(notas)} notas finales calculadas."
        except Exception as e:
            print("Error al cerrar sección:", e)
            return False, HTTP_BAD_REQUEST

    def generar_reporte_notas_seccion(self, section_id: int):
        try:
            self.cursor.execute("""
                SELECT st.student_id, st.name AS student_name,
                       ev.evaluation_id, ev.type AS eval_type, ev.weight AS eval_weight,
                       ei.name AS instance_name, ei.specific_weight, g.score
                FROM students st
                JOIN enrollments e ON st.student_id = e.student_id
                JOIN grades g ON e.enrollment_id = g.enrollment_id
                JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
                JOIN evaluations ev ON ei.evaluation_id = ev.evaluation_id
                WHERE ev.section_id = %s
                ORDER BY st.name, ev.evaluation_id, ei.instance_eval_id
            """, (section_id,))
            rows = self.cursor.fetchall()

            from collections import defaultdict
            data_por_estudiante = defaultdict(lambda: defaultdict(list))

            for row in rows:
                student = row["student_name"]
                eval_id = row["evaluation_id"]
                data_por_estudiante[student][eval_id].append({
                    "type": row["eval_type"],
                    "weight": row["eval_weight"],
                    "instance_name": row["instance_name"],
                    "specific_weight": row["specific_weight"],
                    "score": row["score"]
                })

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Reporte de Notas por Evaluación", ln=True, align='C')
            pdf.ln(10)

            for student, evaluaciones in data_por_estudiante.items():
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(200, 10, txt=f"Estudiante: {student}", ln=True)

                pdf.set_font("Arial", 'B', 10)
                pdf.cell(70, 8, txt="Evaluación", border=1)
                pdf.cell(70, 8, txt="Instancia", border=1)
                pdf.cell(30, 8, txt="Peso", border=1)
                pdf.cell(20, 8, txt="Nota", border=1, ln=True)

                for eval_id, instancias in evaluaciones.items():
                    for instancia in instancias:
                        score = instancia["score"]
                        try:
                            score = float(score)
                            if score < 1.0 or score > 7.0:
                                score = 1.0
                        except:
                            score = 1.0
                        pdf.set_font("Arial", '', 10)
                        pdf.cell(70, 8, txt=instancia["type"], border=1)
                        pdf.cell(70, 8, txt=instancia["instance_name"], border=1)
                        pdf.cell(30, 8, txt=str(instancia["specific_weight"]), border=1)
                        pdf.cell(20, 8, txt=str(round(score, 2)), border=1, ln=True)

                pdf.ln(5)

            path = f"/tmp/reporte_notas_seccion_{section_id}.pdf"
            pdf.output(path)
            return path

        except Exception as e:
            print("Error generando reporte notas sección:", e)
            return None

    def generar_reporte_notas_finales(self, section_id: int):
        try:
            self.cursor.execute("""
                SELECT st.student_id, st.name AS student_name,
                       ev.evaluation_id, ev.weight AS eval_weight,
                       g.score, ei.specific_weight
                FROM students st
                JOIN enrollments e ON st.student_id = e.student_id
                JOIN grades g ON g.enrollment_id = e.enrollment_id
                JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
                JOIN evaluations ev ON ei.evaluation_id = ev.evaluation_id
                WHERE ev.section_id = %s
                ORDER BY st.name, ev.evaluation_id, ei.instance_eval_id
            """, (section_id,))
            rows = self.cursor.fetchall()

            from collections import defaultdict
            data_por_estudiante = defaultdict(lambda: defaultdict(list))

            for row in rows:
                student = row["student_name"]
                eval_id = row["evaluation_id"]
                data_por_estudiante[student][eval_id].append({
                    "score": row["score"],
                    "specific_weight": row["specific_weight"],
                    "eval_weight": row["eval_weight"]
                })

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Reporte de Notas Finales", ln=True, align='C')

            pdf.ln(10)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(100, 10, "Alumno", border=1)
            pdf.cell(40, 10, "Nota Final", border=1, ln=True)

            for student, evaluaciones in data_por_estudiante.items():
                nota_final = 0.0
                for eval_id, instancias in evaluaciones.items():
                    subtotal = 0.0
                    peso_eval = instancias[0]["eval_weight"]
                    for instancia in instancias:
                        score = instancia["score"]
                        try:
                            score = float(score)
                            if score < 1.0 or score > 7.0:
                                score = 1.0
                        except:
                            score = 1.0
                        subtotal += score * instancia["specific_weight"]
                    nota_final += subtotal * peso_eval

                pdf.set_font("Arial", '', 11)
                pdf.cell(100, 10, str(student), border=1)
                pdf.cell(40, 10, str(round(nota_final, 2)), border=1, ln=True)

            path = f"/tmp/reporte_finales_seccion_{section_id}.pdf"
            pdf.output(path)
            return path

        except Exception as e:
            print("Error generando reporte notas finales:", e)
            return None

    def generar_certificado_por_alumno(self, section_id: int, student_id: int):
        try:
            # Paso 1: obtener los datos necesarios
            self.cursor.execute("""
                SELECT st.name AS student_name, c.name AS course_name, c.code,
                    ev.evaluation_id, ev.type AS eval_type, ev.weight AS eval_weight,
                    ei.name AS instance_name, ei.specific_weight, g.score
                FROM students st
                JOIN enrollments e ON st.student_id = e.student_id
                JOIN grades g ON e.enrollment_id = g.enrollment_id
                JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
                JOIN evaluations ev ON ei.evaluation_id = ev.evaluation_id
                JOIN sections s ON ev.section_id = s.section_id
                JOIN course_instances ci ON s.instance_id = ci.instance_id
                JOIN courses c ON ci.course_id = c.course_id
                WHERE s.section_id = %s AND st.student_id = %s
                ORDER BY ev.evaluation_id, ei.instance_eval_id
            """, (section_id, student_id))
            rows = self.cursor.fetchall()
            if not rows:
                return None

            student_name = rows[0]["student_name"]
            course_name = rows[0]["course_name"]
            course_code = rows[0]["code"]

            # Agrupar datos por evaluación
            from collections import defaultdict
            evaluaciones = defaultdict(lambda: {"type": "", "weight": 0.0, "instancias": []})

            for row in rows:
                eval_id = row["evaluation_id"]
                evaluaciones[eval_id]["type"] = row["eval_type"]
                evaluaciones[eval_id]["weight"] = row["eval_weight"]
                evaluaciones[eval_id]["instancias"].append({
                    "name": row["instance_name"],
                    "score": row["score"],
                    "specific_weight": row["specific_weight"]
                })

            # Calcular promedio por evaluación y promedio final
            promedios_evaluacion = {}
            nota_final = 0.0

            for eval_id, data in evaluaciones.items():
                subtotal = 0.0
                for inst in data["instancias"]:
                    subtotal += inst["score"] * inst["specific_weight"]
                promedios_evaluacion[eval_id] = subtotal
                nota_final += subtotal * data["weight"]

            # Generar PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Certificado de Notas", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, txt=f"Estudiante: {student_name}", ln=True)
            pdf.cell(200, 10, txt=f"Curso: {course_name} ({course_code})", ln=True)
            pdf.cell(200, 10, txt=f"Nota Final: {round(nota_final, 2)}", ln=True)

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Detalle de Evaluaciones:", ln=True)

            pdf.set_font("Arial", 'B', 11)
            pdf.cell(70, 8, txt="Tipo", border=1)
            pdf.cell(60, 8, txt="Instancia", border=1)
            pdf.cell(30, 8, txt="Peso %", border=1)
            pdf.cell(30, 8, txt="Nota", border=1, ln=True)

            pdf.set_font("Arial", '', 11)
            for eval_id, data in evaluaciones.items():
                for inst in data["instancias"]:
                    pdf.cell(70, 8, txt=data["type"], border=1)
                    pdf.cell(60, 8, txt=inst["name"], border=1)
                    pdf.cell(30, 8, txt=str(round(inst["specific_weight"], 2)), border=1)
                    pdf.cell(30, 8, txt=str(round(inst["score"], 2)), border=1, ln=True)

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Promedios por Tipo de Evaluación:", ln=True)
            pdf.set_font("Arial", '', 11)
            for eval_id, prom in promedios_evaluacion.items():
                tipo = evaluaciones[eval_id]["type"]
                pdf.cell(200, 8, txt=f"{tipo}: {round(prom, 2)}", ln=True)

            path = f"/tmp/certificado_alumno_{student_id}_seccion_{section_id}.pdf"
            pdf.output(path)
            return path

        except Exception as e:
            print("Error generando certificado alumno:", e)
            return None
    
    def generar_reporte_resumen_por_estudiante(self, student_id: int):
        try:
            self.cursor.execute("""
                SELECT st.name AS student_name, c.name AS course_name, c.code, s.section_id,
                    ev.evaluation_id, ev.type AS eval_type, ev.weight AS eval_weight,
                    ei.name AS instance_name, ei.specific_weight, g.score
                FROM students st
                JOIN enrollments e ON st.student_id = e.student_id
                JOIN sections s ON e.section_id = s.section_id
                JOIN grades g ON e.enrollment_id = g.enrollment_id
                JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
                JOIN evaluations ev ON ei.evaluation_id = ev.evaluation_id
                JOIN course_instances ci ON s.instance_id = ci.instance_id
                JOIN courses c ON ci.course_id = c.course_id
                WHERE st.student_id = %s AND s.closed = TRUE
                ORDER BY c.name, ev.evaluation_id, ei.instance_eval_id
            """, (student_id,))
            rows = self.cursor.fetchall()
            if not rows:
                return None

            from collections import defaultdict
            cursos = defaultdict(lambda: {
                "nombre": "",
                "codigo": "",
                "evaluaciones": defaultdict(lambda: {
                    "type": "", "weight": 0.0, "instancias": []
                })
            })

            student_name = rows[0]["student_name"]

            for row in rows:
                course = row["course_name"]
                code = row["code"]
                eval_id = row["evaluation_id"]
                cursos[course]["nombre"] = course
                cursos[course]["codigo"] = code
                cursos[course]["evaluaciones"][eval_id]["type"] = row["eval_type"]
                cursos[course]["evaluaciones"][eval_id]["weight"] = row["eval_weight"]
                cursos[course]["evaluaciones"][eval_id]["instancias"].append({
                    "name": row["instance_name"],
                    "score": row["score"],
                    "specific_weight": row["specific_weight"]
                })

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Resumen Académico del Estudiante", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, txt=f"Nombre: {student_name}", ln=True)
            pdf.ln(5)

            promedio_global = 0.0
            cantidad_cursos = 0

            for curso, info in cursos.items():
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(200, 10, txt=f"{info['nombre']} ({info['codigo']})", ln=True)

                pdf.set_font("Arial", 'B', 11)
                pdf.cell(70, 8, "Tipo", border=1)
                pdf.cell(60, 8, "Instancia", border=1)
                pdf.cell(30, 8, "Peso %", border=1)
                pdf.cell(30, 8, "Nota", border=1, ln=True)

                nota_final = 0.0

                for eval_id, eval_data in info["evaluaciones"].items():
                    subtotal = 0.0
                    for inst in eval_data["instancias"]:
                        score = inst["score"]
                        try:
                            score = float(score)
                            if score < 1.0 or score > 7.0:
                                score = 1.0
                        except:
                            score = 1.0
                        subtotal += score * inst["specific_weight"]
                        pdf.set_font("Arial", '', 11)
                        pdf.cell(70, 8, txt=eval_data["type"], border=1)
                        pdf.cell(60, 8, txt=inst["name"], border=1)
                        pdf.cell(30, 8, txt=str(round(inst["specific_weight"], 2)), border=1)
                        pdf.cell(30, 8, txt=str(round(score, 2)), border=1, ln=True)

                    nota_final += subtotal * eval_data["weight"]

                pdf.cell(200, 8, txt=f"Nota final del curso: {round(nota_final, 2)}", ln=True)
                pdf.ln(5)
                promedio_global += nota_final
                cantidad_cursos += 1

            if cantidad_cursos > 0:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(200, 10, txt=f"Promedio General (cursos cerrados): {round(promedio_global / cantidad_cursos, 2)}", ln=True)

            path = f"/tmp/resumen_estudiante_{student_id}.pdf"
            pdf.output(path)
            return path

        except Exception as e:
            print("Error generando resumen por estudiante:", e)
            return None