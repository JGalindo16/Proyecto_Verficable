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


## COSAS A TENER EN CUENTA.

### La base de datos sufrió bastantes cambios, recomendamos botar la base de datos y volverla a crear con los pasos de arriba. 
### No esta de más volver a recordar que se tiene que ejecutar en chrome ya que en algunos navegadore no funciona el tour guído de carga de json's
### En relación con los errores recurrentes señalados por flake8, existen tres casos que tienen una justificación clara: el uso de espacios en blanco se realiza intencionalmente para seccionar el código y mejorar su legibilidad; las líneas largas se mantienen en algunos casos para evitar cortes que dificulten la comprensión del código, priorizando la claridad y la flexibilidad en el formato; y, finalmente, la importación de queries desde archivos externos se debe a que, al ser numerosas, incluirlas todas directamente haría el encabezado del archivo más desordenado y menos legible. Estas prácticas fueron adoptadas deliberadamente para favorecer la organización, limpieza y mantenibilidad del proyecto.
