# 🤖 REGISTRO DE SESIONES DE DESARROLLO CON OPENCODE

**Proyecto:** Sistema de Chocolatería Gourmet con CRUD e IA Local (Ollama)  
**Asignatura:** Programación IV — Entregable Final  
**Estudiante:** Fernando Carlos Carrasco Condori  
**Herramienta Asistente:** OpenCode (Terminal AI Coding Agent)  

---

## 1. DESCRIPCIÓN DEL ENTORNO DE TRABAJO CON OPENCODE

Para el desarrollo del proyecto se utilizó **OpenCode**, un agente de codificación de código abierto que opera directamente desde la interfaz de línea de comandos (CLI/TUI) en un entorno Linux Debian 12 / Windows PowerShell. OpenCode asistió en:
- El diseño y generación del modelo de datos `Producto` con sus validaciones.
- La estructuración de las vistas CRUD y consultas de agregación para los 5 reportes analíticos.
- La construcción del servicio de comunicación con la API de Ollama (`/api/generate`) y serialización del inventario en JSON.
- La generación de pruebas unitarias automatizadas (`tests.py`) y la refactorización para respuestas limpias en español.

---

## 2. SESIONES DE TRABAJO, PROMPTS Y CÓDIGO GENERADO

### Sesión 1: Modelado de Datos y Validaciones del CRUD
**Objetivo:** Diseñar la entidad `Producto` con más de 6 campos, validación de código único y valores no negativos.

- **Prompt enviado a OpenCode:**
```text
opencode run "Necesito crear una app en Django llamada 'productos' para una Chocolatería Gourmet. 
Crea el modelo Producto en productos/models.py con:
- codigo único (ej: CHOC-001)
- nombre (CharField 150)
- descripcion (TextField)
- categoria con choices (Negro, Leche, Blanco, Relleno, Trufas, Gourmet)
- precio en Bs con validador de mínimo 0.0
- cantidad_existente con validador de mínimo 0
- estado (BooleanField activo/inactivo)
- fecha_ingreso (DateField)
- imagen (ImageField a 'productos/')
- porcentaje_cacao y origen_cacao
Incluye métodos __str__ y metadatos verbose_name."
```

- **Respuesta de OpenCode (Extracto):**
```python
# Generado por OpenCode en productos/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class CategoriaChocolate(models.TextChoices):
    NEGRO = 'Negro / Amargo', 'Negro / Amargo (70%+ Cacao)'
    LECHE = 'Con Leche', 'Chocolate con Leche'
    BLANCO = 'Blanco', 'Chocolate Blanco Fino'
    RELLENO = 'Relleno / Bombón', 'Bombones Rellenos'
    TRUFAS = 'Trufas', 'Trufas Artesanales'
    ESPECIAL = 'Edición Especial', 'Edición Especial Cacao Criollo'

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código del Producto")
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Chocolate")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    categoria = models.CharField(max_length=50, choices=CategoriaChocolate.choices, default=CategoriaChocolate.NEGRO)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    cantidad_existente = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    estado = models.BooleanField(default=True)
    fecha_ingreso = models.DateField(default=timezone.now)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    porcentaje_cacao = models.PositiveIntegerField(default=70, blank=True, null=True)
    origen_cacao = models.CharField(max_length=150, default='Bolivia')
```
- **Impacto:** Se obtuvo una estructura de modelo limpia, cumpliendo con la rúbrica y las restricciones de integridad relacional.

---

### Sesión 2: Implementación de los 5 Reportes Analíticos de Inventario
**Objetivo:** Desarrollar consultas agregadas de Django ORM para cumplir el requerimiento de los 5 reportes.

- **Prompt enviado a OpenCode:**
```text
opencode run "En productos/views.py genera una vista reportes_panel(request) que calcule en tiempo real:
1. Productos con stock crítico (< 10 unidades).
2. Estadísticas de precio: máximo, mínimo y promedio usando aggregate() de Django.
3. Total de unidades y valor total monetario agrupado por cada categoría.
4. Total de productos activos vs inactivos.
5. Productos gourmet con 70% o más de cacao.
Retorna todo en el contexto para una plantilla reportes.html."
```

- **Respuesta de OpenCode (Extracto):**
```python
# Generado por OpenCode en productos/views.py
from django.db.models import Max, Min, Avg, Sum

def reportes_panel(request):
    stock_critico = Producto.objects.filter(cantidad_existente__lt=10).order_by('cantidad_existente')
    total_activos = Producto.objects.filter(estado=True).count()
    total_inactivos = Producto.objects.filter(estado=False).count()
    
    stats_precio = Producto.objects.aggregate(
        precio_max=Max('precio'),
        precio_min=Min('precio'),
        precio_promedio=Avg('precio')
    )
    
    alta_pureza = Producto.objects.filter(porcentaje_cacao__gte=70).order_by('-porcentaje_cacao')
    
    categorias_stats = []
    for cat_val, cat_label in CategoriaChocolate.choices:
        prods = Producto.objects.filter(categoria=cat_val)
        if prods.exists():
            categorias_stats.append({
                'nombre': cat_label,
                'cantidad_variedades': prods.count(),
                'total_unidades': prods.aggregate(s=Sum('cantidad_existente'))['s'] or 0,
                'valor_total': sum(p.precio * p.cantidad_existente for p in prods)
            })
    ...
```
- **Impacto:** Código eficiente aprovechando funciones nativas de base de datos de Django sin sobrecargar la memoria.

---

### Sesión 3: Integración de IA Local con Ollama y Restricción a Datos (Grounding)
**Objetivo:** Crear el servicio de conexión a Ollama en `http://localhost:11434/api/generate` inyectando el inventario en formato JSON.

- **Prompt enviado a OpenCode:**
```text
opencode run "Necesito un módulo desacoplado para consultar a Ollama local usando el modelo qwen2.5:1.5b.
Debe:
1. Extraer los productos de SQLite como JSON con sus campos esenciales.
2. Inyectar un System Prompt estricto que obligue a la IA a responder SOLO con datos del JSON en español y negarse a responder si no hay información.
3. Enviar la consulta a http://localhost:11434/api/generate con timeout controlado y manejo de errores."
```

- **Respuesta de OpenCode (Extracto):**
```python
# Generado por OpenCode para la integración con Ollama
def _obtener_inventario_json() -> str:
    productos = Producto.objects.all()
    data = [{
        "cod": p.codigo,
        "nom": p.nombre,
        "cat": p.categoria,
        "precio": float(p.precio),
        "stock": p.cantidad_existente,
        "estado": "Activo" if p.estado else "Inactivo",
        "cacao": f"{p.porcentaje_cacao}%",
        "origen": p.origen_cacao
    } for p in productos]
    return json.dumps(data, ensure_ascii=False)

def consultar_ollama_local(pregunta: str) -> str:
    try:
        inventario = _obtener_inventario_json()
        prompt = f"{SYSTEM_PROMPT_INVENTARIO}\n\nINVENTARIO:\n{inventario}\n\nPREGUNTA:\n{pregunta}"
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": "productos-qwen2.5",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_ctx": 1024}
        }, timeout=45)
        if res.status_code == 200:
            return res.json().get("response", "").strip()
    except Exception:
        pass
    return "No encontré información suficiente en el inventario para responder esa pregunta."
```
- **Impacto:** Se garantizó la restricción de respuestas (Grounding) solicitada en el Punto 2.4 de la rúbrica.

---

### Sesión 4: Pruebas Unitarias Automatizadas
**Objetivo:** Crear la batería de pruebas para validación de código único, precios no negativos y cálculos analíticos.

- **Prompt enviado a OpenCode:**
```text
opencode run "Escribe pruebas unitarias exhaustivas en productos/tests.py utilizando TestCase de Django.
Valida:
- Que no se pueda duplicar el campo 'codigo'.
- Que el validador de precio rechace valores negativos.
- Que el cálculo de stock crítico y agregaciones de reportes funcione con datos de prueba."
```

- **Respuesta de OpenCode (Extracto):**
```python
# Generado por OpenCode en productos/tests.py
class ProductoModelTest(TestCase):
    def test_codigo_unico(self):
        Producto.objects.create(codigo="CHOC-TEST", nombre="Choc 1", precio=Decimal("10.00"), cantidad_existente=5)
        with self.assertRaises(Exception):
            Producto.objects.create(codigo="CHOC-TEST", nombre="Choc 2", precio=Decimal("15.00"), cantidad_existente=10)

    def test_precio_no_negativo(self):
        p = Producto(codigo="CHOC-NEG", nombre="Neg", precio=Decimal("-5.00"), cantidad_existente=1)
        with self.assertRaises(ValidationError):
            p.full_clean()
```
- **Impacto:** Cobertura de pruebas completa y validada exitosamente con `python manage.py test`.

---

## 3. REFLEXIÓN SOBRE EL IMPACTO DE OPENCODE EN EL DESARROLLO

1. **Aceleración del Ciclo de Desarrollo:**  
   OpenCode permitió generar estructuras repetitivas (MVT de Django, migraciones y formularios) de manera rápida y sin errores de sintaxis.
2. **Control de Calidad y Refactorización:**  
   Asistió en la identificación temprana de validaciones críticas en el modelo y en la generación de pruebas unitarias robustas.
3. **Rol del Desarrollador:**  
   Aunque el agente aceleró la generación de código base, el criterio del estudiante fue indispensable para la integración final de la API de Ollama, el afinamiento del System Prompt, la configuración de la base de datos relacional y la estética del frontend con HTMX y TailwindCSS.
