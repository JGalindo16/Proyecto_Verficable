# 🚀 Configuración del Proyecto - POC Verificable
---

## ⚙️ Cómo configurar la base de datos

> 📌 **Requisito:** Asegúrate de tener Docker corriendo antes de continuar. Los pasos para esto están más abajo.

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

## 📊 Scripts de Utilidad

La aplicación incluye scripts de utilidad para facilitar ciertas tareas:

### 📈 Poblar la Base de Datos

El script `scripts/populate_db.py` permite llenar la base de datos con datos de prueba extensos.

#### Características:

- 20 cursos diferentes
- 25 profesores
- 100 estudiantes con datos aleatorios
- Instancias de cursos para 2021-2024 (semestres 1 y 2)
- Entre 1 y 5 secciones por instancia
- Entre 10 y 30 estudiantes por sección
- Evaluaciones (exámenes, controles, tareas, proyectos)
- Miles de notas realistas

#### Para ejecutarlo:

1. Asegúrate de que la base de datos MySQL esté en funcionamiento:
   ```bash
   cd db && docker-compose up -d
   ```

2. Desde el directorio raíz del proyecto, ejecuta:
   ```bash
   cd scripts
   python populate_db.py
   ```

3. Una vez completado, accede a la aplicación en:
   http://localhost:5000


















