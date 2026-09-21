# Registro de Modificaciones (CAMBIOS.md)

Este documento detalla todas las modificaciones, traducciones, ajustes de prompts del sistema y nuevas funcionalidades implementadas sobre el proyecto base de chat local con RAG y Ollama.

---

## 1. Localizacion al Espanol (Internacionalizacion y UI)

### 1.1 Configuracion Global de Idioma (`a_core/settings.py`)
Modifique el archivo de configuracion de Django para definir el espanol como idioma principal del sistema:
```python
# a_core/settings.py
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True
```

### 1.2 Traduccion de la Interfaz y Vistas (`templates/` y `a_rtchat/views.py`)
Traduje todos los textos visibles de la interfaz:
- Formulario de entrada de mensajes: "Escribe tu mensaje o pregunta aqui..."
- Mensajes informativos y de error del sistema cuando la IA no esta disponible.
- Titulos y etiquetas de los botones de accion.

---

## 2. Ajuste del Modelo y Prompts del Sistema (`a_rtchat/rag.py`)

Para asegurar que la IA responda siempre en espanol latino, configure el System Prompt y la plantilla de preguntas y respuestas dentro del modulo RAG:

```python
# a_rtchat/rag.py
SYSTEM_PROMPT_ES = (
    "Eres un asistente virtual inteligente, amigable y servicial. "
    "Responde siempre en espanol latino de forma clara, natural, precisa y concisa. "
    "Si te hacen una pregunta sobre los documentos proporcionados, basate en ellos. "
    "Si te hacen una pregunta general o de conversacion, responde amablemente en espanol latino."
)

TEXT_QA_TEMPLATE_STR = (
    "Informacion de contexto:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Con base en el contexto anterior (y respondiendo amablemente si es una consulta general), "
    "responde a la pregunta siempre en espanol latino de forma clara, precisa y directa.\n"
    "Pregunta: {query_str}\n"
    "Respuesta: "
)
```

---

## 3. Funcionalidades Anadidas

### 3.1 Funcionalidad 1: Modo Dual / Chat General sin Documentos Obligatorios
- **Problema encontrado:** El proyecto original arrojaba un error y se detenia si la carpeta `knowledge_base/` no contenia archivos.
- **Modificacion implementada:** Agregue una logica en `a_rtchat/views.py` para que cuando no haya documentos cargados, el sistema responda directamente con Ollama como un chat general, permitiendo responder cualquier pregunta cotidiana sin bloquearse.

```python
# a_rtchat/views.py
def _answer_question(question: str) -> str:
    try:
        answer = LocalRag.from_settings().answer(question)
    except KnowledgeBaseEmpty:
        # Modo Dual: Responde directamente con Ollama como chat general
        return _answer_with_ollama_directly(question)
    except LocalRagConfigurationError as exc:
        return str(exc)
    except LocalRagError:
        return (
            "No pude procesar tu consulta. "
            "Verifica que Ollama este en ejecucion y que los modelos configurados esten instalados."
        )

    if not answer.sources:
        return answer.text

    sources = ", ".join(answer.sources)
    return f"{answer.text}\n\nFuentes: {sources}"


def _answer_with_ollama_directly(question: str) -> str:
    """Responde directamente usando Ollama cuando no hay documentos indexados."""
    from django.conf import settings as django_settings
    from .rag import SYSTEM_PROMPT_ES

    try:
        from llama_index.llms.ollama import Ollama

        llm = Ollama(
            model=django_settings.OLLAMA_CHAT_MODEL,
            base_url=django_settings.OLLAMA_BASE_URL,
            request_timeout=django_settings.OLLAMA_REQUEST_TIMEOUT,
            system_prompt=SYSTEM_PROMPT_ES,
            context_window=django_settings.OLLAMA_NUM_CTX,
            additional_kwargs={
                "num_ctx": django_settings.OLLAMA_NUM_CTX,
                "num_predict": django_settings.OLLAMA_NUM_PREDICT,
            },
        )
        response = llm.complete(question)
        return str(response)
    except Exception as exc:
        return f"Error al procesar la consulta con la IA: {exc}"
```

### 3.2 Funcionalidad 2: Optimizacion de Rendimiento y Soporte del Modelo Ligero (`qwen2.5:1.5b`)
- **Problema encontrado:** El modelo por defecto de 3B sobrepasaba la memoria grafica, tardaba entre 3 y 4 minutos por respuesta en CPU o daba timeout.
- **Modificacion implementada:** Configure soporte para `qwen2.5:1.5b` en el archivo `.env`, limitando ademas el contexto (`num_ctx = 2048`), la cantidad de tokens (`num_predict = 80`) y el timeout (`request_timeout = 360.0`), logrando reducir el tiempo de respuesta a menos de un minuto con total estabilidad.

---

## 4. Archivos Modificados y Creados

| Archivo | Tipo de Cambio | Descripcion |
| :--- | :--- | :--- |
| `a_core/settings.py` | Modificado | Configuracion de idioma en espanol (`LANGUAGE_CODE = 'es'`). |
| `a_rtchat/rag.py` | Modificado | Prompts en espanol y plantillas de respuesta. |
| `a_rtchat/views.py` | Modificado | Implementacion del chat directo sin documentos y manejo de errores. |
| `.env` / `envtemp` | Modificado | Parametros configurados para el modelo liviano `qwen2.5:1.5b`. |
| `README.md` | Modificado | Documentacion traducida al espanol y guia de optimizacion con `qwen2.5:1.5b`. |
| `CAMBIOS.md` | Creado | Registro de modificaciones realizadas. |
| `informe.md` | Creado | Informe tecnico en formato Markdown. |
