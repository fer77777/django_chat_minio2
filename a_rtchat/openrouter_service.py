import json
import logging
import requests
from django.conf import settings
from productos.models import Producto

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT_INVENTARIO = """Eres el Asistente Virtual Inteligente de la Chocolatería Gourmet Artesanal.
Tu tarea es responder preguntas sobre los productos, catálogo, precios, existencias y características de los chocolates registrados.

REGLAS:
1. Responde de forma directa y concisa en español latino amigable.
2. Utiliza los datos del INVENTARIO JSON provisto.
3. Si la pregunta no está relacionada con la chocolatería o su inventario, responde:
   "No encontré información suficiente en el inventario para responder esa pregunta."
4. NO muestres tu proceso de razonamiento ni etiquetas técnicas. Responde directamente la respuesta final al usuario.
"""


def _obtener_inventario_json() -> str:
    """Extrae todos los productos registrados en formato JSON compacto y rápido."""
    productos = Producto.objects.all()
    if not productos.exists():
        return "[]"

    data = []
    for p in productos:
        data.append({
            "cod": p.codigo,
            "nom": p.nombre,
            "cat": p.categoria,
            "precio": float(p.precio),
            "stock": p.cantidad_existente,
            "estado": "Activo" if p.estado else "Inactivo",
            "cacao": f"{p.porcentaje_cacao}%" if getattr(p, 'porcentaje_cacao', None) else None,
            "origen": getattr(p, 'origen_cacao', 'Bolivia')
        })
    return json.dumps(data, ensure_ascii=False)


# Modelos gratuitos conversacionales en español
MODELOS_GRATUITOS = [
    "liquid/lfm-2.5-2.6b:free",
    "openrouter/free",
    "google/gemma-4-31b-it:free",
]


def consultar_openrouter(pregunta: str) -> str:
    """Envía la consulta a OpenRouter con timeout corto y fallback automático a Ollama local."""
    api_key = getattr(settings, 'OPENROUTER_API_KEY', '') or ''
    if not api_key:
        return _fallback_ollama_local(pregunta)

    inventario_json = _obtener_inventario_json()
    total_productos = Producto.objects.count()

    prompt_completo = f"""INVENTARIO ({total_productos} productos):
{inventario_json}

PREGUNTA: {pregunta}"""

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:8000",
        "X-Title": "Chocolateria Gourmet",
    }

    config_model = getattr(settings, 'OPENROUTER_MODEL', '')
    modelos_a_probar = [config_model] if config_model and config_model not in MODELOS_GRATUITOS else []
    modelos_a_probar.extend([m for m in MODELOS_GRATUITOS if m not in modelos_a_probar])

    for modelo in modelos_a_probar:
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_INVENTARIO},
                {"role": "user", "content": prompt_completo},
            ],
            "temperature": 0.1,
            "max_tokens": 800,
        }

        try:
            # Timeout de 10 segundos por modelo
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices")
                if choices and len(choices) > 0:
                    msg = choices[0].get("message", {})
                    content = msg.get("content")
                    # Si el modelo guardó la respuesta solo en content
                    if content and isinstance(content, str) and content.strip():
                        texto = content.strip()
                        # Si por algún motivo el modelo pegó reasoning en el texto, limpiarlo:
                        if "Here's a thinking process:" in texto:
                            partes = texto.split("\n\n")
                            texto = partes[-1] if len(partes) > 1 else texto
                        return texto
                    
                    # Si el content vino vacío o truncado por reasoning, no mostrar el reasoning en inglés
        except Exception:
            continue

    # Si OpenRouter está saturado o da rate limit (429), responder con Ollama local de inmediato
    return _fallback_ollama_local(pregunta)


def _fallback_ollama_local(pregunta: str) -> str:
    """Fallback directo a Ollama local con parámetros optimizados de velocidad."""
    try:
        inventario_json = _obtener_inventario_json()
        prompt_completo = f"{SYSTEM_PROMPT_INVENTARIO}\n\nINVENTARIO:\n{inventario_json}\n\nPREGUNTA:\n{pregunta}"
        modelo_local = getattr(settings, "OLLAMA_CHAT_MODEL", "qwen2.5:1.5b")
        
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": modelo_local,
            "prompt": prompt_completo,
            "stream": False,
            "options": {
                "num_predict": 120,
                "num_ctx": 1024,
                "temperature": 0.1,
            }
        }, timeout=45)

        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception as exc:
        logger.warning(f"Ollama local no disponible: {exc}")

    return "No encontré información suficiente en el inventario para responder esa pregunta."
