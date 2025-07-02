# LEER TODO EL README ANTES DE EJECUTAR CUALQUIER COSA.
---
# 🚀 Configuración del Proyecto - POC Verificable
---

## ⚙️ Cómo configurar la base de datos

> 📌 **Requisito:** Asegúrate de tener Docker corriendo antes de continuar. Los pasos para esto están más abajo.

> 📌 **Requisito:** Porfavor ocupen google chrome ya que hicimos un tour guiado para que puedan cargar los archivos JSON en el orden correcto. Esto no funciona en safari.

### 1. Cargar las tablas

Desde la raíz del proyecto, ejecutá el siguiente comando para importar el esquema SQL:

```bash
mysql -h 127.0.0.1 -P 3307 -u user -p test_poc < db/db.sql
```

La contraseña por defecto es: **`pass`**

---

### 2. Verificar que las tablas se hayan creado

Ingresa al cliente de MySQL:

```bash
mysql -h 127.0.0.1 -P 3307 -u user -p
```

Una vez dentro:

```sql
USE test_poc;
SHOW TABLES;
```

Si ves las tablas listadas, ¡todo está correcto!

---

## 🐳 Cómo levantar el entorno de desarrollo

> ⚠️ **Nota importante:** Para trabajar correctamente, vas a necesitar **dos terminales abiertas**.

---

### 🖥 Terminal 1 — Levantar MySQL con Docker

Ir a la carpeta `db` y ejecutar:

```bash
docker-compose up
```

🛑 Esta terminal debe quedar abierta y corriendo en segundo plano mientras trabajás.

---

### 🖥 Terminal 2 — Correr la app Flask

#### 1. Crear el entorno virtual (solo la primera vez):

```bash
python -m venv venv
```

#### 2. Activar el entorno virtual:

```bash
. venv/bin/activate
```

*(En Windows: `venv\Scripts\activate`)*

#### 3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

> Repetir este comando cada vez que se actualice el archivo `requirements.txt`.

#### 4. Ejecutar la aplicación:

```bash
python main.py
```

---
## Coverage del proyecto

<img width="1240" alt="Captura de pantalla 2025-06-18 a la(s) 5 28 47 p m" src="https://github.com/user-attachments/assets/9c224c2c-73f6-4b93-95ae-28596b2bdba0" />

## Para Hacer el Analisis estático

Se debe oocupar el siguiente comando:

```bash
flake8
```

> Este tiene la configuración prehecha para ver las complejidades que no sean mayores a 12 además de saltarse las advertencias que especificamos más abajo.

## COSAS A TENER EN CUENTA.

### La base de datos sufrió bastantes cambios, recomendamos botar la base de datos y volverla a crear con los pasos de arriba. 
### No esta de más volver a recordar que se tiene que ejecutar en chrome ya que en algunos navegadore no funciona el tour guído de carga de json's

---
## Justificación errores estaticos (con flake8)

Los errores existentes son los siguientes

- W291 trailing whitespace
- W292 no newline at end of file
- W293 blank line contains whitespace
- E128 continuation line under-indented for visual indent
- E302 expected 2 blank lines, found 1
- E305 expected 2 blank lines after class or function definition, found 1
- E501 line too long (> 79 characters)
- E126 Over-indented for hanging indent
- E129 visually indented line with same indent as next logical line
- E131 continuation line unaligned for hanging indent
- W504 line break after binary operator


En relación con los errores recurrentes señalados por flake8, existen varias advertencias que han sido mantenidas intencionalmente por razones de estilo, claridad y mantenibilidad del proyecto. Por ejemplo, los espacios en blanco innecesarios (W291, W293) y las líneas en blanco al final de archivo (W292) se usan estratégicamente para seccionar el código y mejorar su organización visual. Las líneas largas (E501) se conservan en ciertos casos para evitar cortes que dificulten la comprensión del código, especialmente en sentencias SQL complejas o llamadas con múltiples argumentos, priorizando así la claridad. Los errores relacionados con la cantidad de líneas en blanco (E302, E305) también se ajustaron a un estilo deliberado que favorece la legibilidad local de funciones y clases. Asimismo, la advertencia E128 sobre indentación visual responde a una alineación clara respecto al contexto del bloque.

A modo de resumen, estas se omitieron al ser cosas visuales que no producen una molestia clara al código y es más creemos que son cosas que ayudan a la legibilidad
y entendimiento claro del código.

