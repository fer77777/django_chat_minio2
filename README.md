# 🤖 Django Local RAG Chat (en Español)

Aplicación web de chat local con **RAG (Retrieval-Augmented Generation)** construida sobre **Django 5.2**, **LlamaIndex**, **MarkItDown** y **Ollama**. Permite realizar consultas sobre documentos propios (PDF, DOCX, XLSX, TXT, etc.) y mantener conversaciones de manera 100% local, privada y **completamente en español latino**.

---

## 🌎 Idioma y Configuración en Español

- **Interfaz Web:** Todos los menús, formularios y mensajes están en **español** (`LANGUAGE_CODE = 'es'`).
- **IA en español:** El modelo responde siempre de forma natural y clara en **español latino**.
- **Sin documentos obligatorios:** Puedes chatear normalmente con la IA sin tener archivos en `knowledge_base/`. Si hay documentos, la IA los usa para responder con más precisión.

---

## 📋 Requisitos Previos

1. **Python:** Versión `3.11` o superior (verificado con Python 3.12).
2. **Ollama:** Descargar desde [ollama.com/download](https://ollama.com/download) o instalar con:
   ```powershell
   winget install Ollama.Ollama
   ```
3. **Git:** Para clonar el repositorio.

---

## 🚀 Guía de Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/dilancroos/django_chat.git
cd django_chat
```

---

### 2. Crear y Activar el Entorno Virtual

- **En Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
  > Si PowerShell bloquea la ejecución de scripts, ejecuta primero:
  > ```powershell
  > Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  > ```

- **En Windows (CMD):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate.bat
  ```

- **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

---

### 3. Instalar Dependencias
Con el entorno virtual activado:
```bash
pip install -r requirements.txt
```

---

### 4. Configurar las Variables de Entorno (`.env`)
Copia la plantilla `envtemp` a un nuevo archivo `.env`:

- **En Windows (PowerShell):**
  ```powershell
  Copy-Item envtemp .env
  ```
- **En Linux / macOS:**
  ```bash
  cp envtemp .env
  ```

Contenido por defecto de `.env`:
```ini
DJANGO_SECRET_KEY=django-insecure-local-dev-key-change-me
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2:1b
OLLAMA_EMBED_MODEL=nomic-embed-text
RAG_SOURCE_DIR=knowledge_base
RAG_MARKDOWN_DIR=knowledge_markdown
RAG_STORAGE_DIR=rag_storage
```

> **Nota:** Se recomienda usar `llama3.2:1b` (modelo liviano de 1B parámetros) en lugar de `llama3.2` (3B), ya que el modelo grande puede fallar en GPUs con poca VRAM.

---

### 5. Configurar e Iniciar Ollama

Asegúrate de que Ollama esté instalado y en ejecución, luego descarga los modelos:

```powershell
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

> **⚠️ Problema frecuente en Windows:** Si la terminal no reconoce el comando `ollama` después de instalarlo, es porque el `PATH` no se actualizó en la sesión actual. Solución: actualiza el PATH en esa misma terminal con:
> ```powershell
> $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
> ```
> O simplemente **abre una nueva terminal** y vuelve a intentarlo.

#### ¿Error de memoria de GPU? (CUDA out of memory)
Si Ollama falla con un mensaje de `out of memory`, tienes dos opciones:

**Opción A (Recomendada): Usar el modelo liviano**
```powershell
ollama pull llama3.2:1b
```
Y en `.env` cambia la línea a: `OLLAMA_CHAT_MODEL=llama3.2:1b`

**Opción B: Forzar ejecución en CPU (sin GPU)**
```powershell
$env:OLLAMA_NUM_GPU=0
```
Luego reinicia Ollama.

#### Eliminar un modelo que ya no necesitas
Si descargaste el modelo grande y ya no lo usas, puedes liberarlo del disco:
```powershell
ollama rm llama3.2
```

---

### 6. Ejecutar las Migraciones de Base de Datos
```bash
python manage.py migrate
```

*(Opcional)* Crear un superusuario para el panel de administración (`/admin`):
```bash
python manage.py createsuperuser
```

---

### 7. Agregar Documentos a la Base de Conocimiento (Opcional)
La IA puede responder **sin documentos** (conocimiento general). Si quieres que responda sobre tus propios archivos, colócalos en:
```
knowledge_base/
```

Formatos compatibles: `.pdf`, `.docx`, `.xlsx`, `.xls`, `.pptx`, `.csv`, `.txt`, `.md`, `.html`, `.json`, `.xml`, `.zip`, `.epub`.

El sistema convierte automáticamente los documentos a Markdown con **MarkItDown** y los indexa en `rag_storage/`.

---

### 8. Iniciar el Servidor de Desarrollo
```bash
python manage.py runserver
```

Abre tu navegador web en:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 💬 Modos de Respuesta de la IA

| Situación | Comportamiento |
| :--- | :--- |
| `knowledge_base/` **vacía** | La IA responde con su conocimiento general en español |
| `knowledge_base/` **con archivos** | La IA busca en tus documentos y responde citando las fuentes |

---

## 🛠️ Estructura del Proyecto

- `a_core/`: Configuración principal de Django (`settings.py`, `urls.py`).
- `a_rtchat/`: Lógica del chat y flujo RAG con LlamaIndex y prompts en español.
- `a_users/`: Gestión de perfiles y usuarios.
- `a_home/`: Vistas de inicio.
- `knowledge_base/`: Carpeta donde colocar los documentos fuente a indexar.
- `knowledge_markdown/`: Documentos convertidos a Markdown.
- `rag_storage/`: Índice vectorial generado por LlamaIndex.
- `templates/` & `static/`: Plantillas HTML y archivos estáticos.

---

## 🧪 Verificar que todo funciona

```bash
python manage.py check
```

---

## ⚡ Optimización de Velocidad (Reducir Tiempo de Respuesta)

Si la IA tarda mucho en responder (ej. más de 30-60 segundos), se debe a alguno de estos factores:

1. **Tamaño del Modelo (El factor principal):**
   - El modelo `llama3.2` (3B) requiere mucha memoria. Si no cabe en la tarjeta gráfica (GPU), se ejecuta en el procesador (CPU) y puede tardar de 1 a 3 minutos por mensaje.
   - **Solución:** Usar `llama3.2:1b` en tu archivo `.env`. Al ser de 1B de parámetros, responde en **pocos segundos** (3-10x más rápido).

2. **Carga inicial en memoria (Cold Start):**
   - El **primer mensaje** tras iniciar Ollama tarda unos segundos extra porque debe cargar los pesos del modelo del disco a la memoria RAM/VRAM. Los mensajes siguientes son mucho más rápidos.

3. **Aceleración por GPU:**
   - Si tu equipo cuenta con tarjeta gráfica dedicada (NVIDIA / AMD), asegúrate de que Ollama no tenga forzado `$env:OLLAMA_NUM_GPU=0`. `llama3.2:1b` cabe perfectamente en cualquier GPU de 2GB a 4GB+ y responderá casi instantáneamente.

---

## 💡 Solución de Problemas Frecuentes

1. **`ollama` no se reconoce como comando después de instalar:**
   - Actualiza el PATH en la terminal actual:
     ```powershell
     $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
     ```
   - O abre una nueva ventana de terminal.

2. **Error de memoria de GPU (`CUDA out of memory`):**
   - Usa el modelo liviano: `ollama pull llama3.2:1b` y cambia `.env` a `OLLAMA_CHAT_MODEL=llama3.2:1b`.
   - O fuerza CPU: `$env:OLLAMA_NUM_GPU=0` y reinicia Ollama.

3. **La IA tarda mucho en responder (2-3 minutos):**
   - Asegúrate de tener configurado `OLLAMA_CHAT_MODEL=llama3.2:1b` en tu archivo `.env`.
   - Reinicia el servidor Django (`python manage.py runserver`).
   - El modelo `1b` es ligero y reduce el tiempo a solo unos segundos.

4. **Error de conexión con Ollama (`Connection Refused`):**
   - Verifica que la app Ollama esté abierta, o ejecuta `ollama serve` en una terminal aparte.

5. **Modelo no encontrado (`model not found`):**
   - Ejecuta `ollama pull llama3.2:1b` y `ollama pull nomic-embed-text`.

6. **Restricción de scripts en PowerShell al activar `.venv`:**
   - Ejecuta: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

7. **Liberar espacio eliminando modelos no usados:**
   ```powershell
   ollama rm llama3.2
   ```

