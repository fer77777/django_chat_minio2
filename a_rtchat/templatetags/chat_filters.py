import re
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown_bold')
def markdown_bold(value):
    """
    Convierte el formato **texto** en <strong>texto</strong> seguro para HTML.
    Escapa el texto general para prevenir inyecciones y solo permite la etiqueta <strong>.
    """
    if not value:
        return ""
    
    # 1. Escapar caracteres HTML peligrosos
    escaped = escape(str(value))
    
    # 2. Reemplazar **texto** por <strong class="font-bold text-amber-200">texto</strong>
    # Usar función de reemplazo para evitar que el signo $ sea interpretado como grupo de captura en regex
    pattern = re.compile(r'\*\*(.+?)\*\*')
    html = pattern.sub(lambda m: f'<strong class="font-bold text-amber-200">{m.group(1)}</strong>', escaped)
    
    # 3. Retornar como HTML seguro
    return mark_safe(html)
