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

## COSAS A TENER EN CUENTA.

### La base de datos sufrió bastantes cambios, recomendamos botar la base de datos y volverla a crear con los pasos de arriba. 
### No esta de más volver a recordar que se tiene que ejecutar en chrome ya que en algunos navegadore no funciona el tour guído de carga de json's
