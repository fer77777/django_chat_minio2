# Entregable Final - Programación IV: Arquitectura y Decisiones Técnicas

**Estudiante:** Fernando Carlos Carrasco Condori  
**Asignatura:** Programación IV  
**Docente:** Ing. de la Materia  
**Proyecto:** Sistema de Gestión de Chocolatería Gourmet con CRUD e IA Local (Ollama)  

---

## 1. Descripción General del Proyecto

Se ha diseñado e implementado una solución web completa con **Django 5.2**, orientada a la administración comercial y de inventarios para una **Chocolatería Artesanal Gourmet**. La aplicación incorpora operaciones **CRUD** exhaustivas, validaciones de modelo y formulario, panel analítico de reportes predefinidos e integración con **IA local mediante Ollama** (asistido en su desarrollo por **OpenCode**).

---

## 2. Decisiones Arquitectónicas y Patrones de Diseño

En cumplimiento de las buenas prácticas de desarrollo de software (Punto 3.1):

1. **Patrón Strategy (Estrategia):**
   - **En el Servicio de IA (`a_rtchat/openrouter_service.py` y `views.py`):** Desacoplamiento del proveedor de inferencia mediante la variable de entorno `AI_PROVIDER`. Permite ejecutar la inferencia de manera 100% local y soberana mediante Ollama (`http://localhost:11434`), con soporte de conmutación a APIs cloud según los recursos de cómputo disponibles.
   - **En el Módulo de Reportes:** Encapsulamiento de las métricas de inventario mediante agregaciones del ORM (`Max`, `Min`, `Avg`, `Sum`).

2. **Patrón Template Method / MVT (Model-View-Template):**
   - Estructuración estándar de Django que separa la lógica de acceso a datos (`models.py`), los controladores de negocio (`views.py`) y las vistas de usuario (`templates/`).

3. **Arquitectura 12-Factor App (Seguridad y Variables de Entorno):**
   - Aislamiento de configuraciones sensibles en `.env` (ignorado en Git mediante `.gitignore`), proveyendo una plantilla oficial `.env.example` para su fácil despliegue.

---

## 3. Modelo de Datos (`Producto`)

El modelo `Producto` se encuentra en `productos/models.py` y cuenta con 10 campos que superan el mínimo de 6 solicitado en la rúbrica:

| N° | Campo | Tipo Django | Validación / Restricción | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `codigo` | `CharField(max_length=50)` | `unique=True` (Obligatorio) | Identificador único del chocolate (ej. `CHOC-001`). |
| 2 | `nombre` | `CharField(max_length=150)` | Obligatorio | Nombre comercial del producto artesanal. |
| 3 | `descripcion` | `TextField` | Opcional | Notas de cata, perfil sensorial y detalles del producto. |
| 4 | `categoria` | `CharField(choices=...)` | Opciones predefinidas | Negro/Amargo, Con Leche, Blanco, Relleno/Bombón, Trufas, Edición Especial. |
| 5 | `precio` | `DecimalField` | `MinValueValidator(0.0)` | Precio unitario no negativo en Bolivianos (Bs.). |
| 6 | `cantidad_existente` | `PositiveIntegerField` | `MinValueValidator(0)` | Unidades físicas disponibles en depósito. |
| 7 | `estado` | `BooleanField` | Default: `True` | Estado activo o inactivo (descontinuado) para la venta. |
| 8 | `fecha_ingreso` | `DateField` | Default: `timezone.now` | Fecha de registro del lote en el inventario. |
| 9 | `imagen` | `ImageField(upload_to='productos/')` | Opcional | Fotografía del producto almacenada en `media/productos/`. |
| 10 | `porcentaje_cacao` | `PositiveIntegerField` | Rango de 0 a 100% | Porcentaje de pureza de grano de cacao. |
| 11 | `origen_cacao` | `CharField` | Texto | Región geográfica de procedencia (ej. Alto Beni, Caranavi). |

---

## 4. Funcionalidades del Módulo CRUD

1. **Catálogo Principal (`/productos/`)**:
   - Tarjetas responsivas con imagen del producto, código, categoría y precio.
   - Buscador en tiempo real por nombre y código.
   - Filtro por categoría y estado de disponibilidad.
   - Alertas visuales destacadas para productos con **stock crítico** (< 10 unidades).

2. **Creación de Producto (`/productos/crear/`)**:
   - Validación de unicidad de código antes de persistir.
   - Bloqueo de precios o cantidades negativas mediante validaciones de formulario (`forms.py`).

3. **Ficha de Detalle (`/productos/<id>/`)**:
   - Especificaciones completas, procedencia del cacao, pureza y valoración monetaria total del lote en stock.

4. **Modificación (`/productos/<id>/editar/`)**:
   - Edición controlada de atributos con mensajes de retroalimentación (Django Messages Framework).

5. **Eliminación (`/productos/<id>/eliminar/`)**:
   - Pantalla de confirmación para evitar borrados accidentales de inventario.

---

## 5. Módulo de Reportes Analíticos (`/productos/reportes/`)

Reportes predefinidos calculados con el ORM de Django:
1. **Alerta de Stock Crítico:** Identificación de lotes con existencias inferiores a 10 unidades.
2. **Precios Extremos y Promedio:** Cálculo de valor máximo, mínimo y promedio ponderado (`Max`, `Min`, `Avg`).
3. **Distribución y Valoración por Categoría:** Conteo de variedades, suma de piezas y capital total invertido (`precio × stock`).
4. **Disponibilidad:** Balance entre productos activos vs. descontinuados.
5. **Línea Gourmet Alta Pureza:** Selección de chocolates con 70% o más de cacao silvestre boliviano.

---

## 6. Pruebas Unitarias (`productos/tests.py`)

Se implementaron pruebas automatizadas que verifican la integridad del sistema:
- `test_codigo_unico`: Garantiza que el sistema lance `IntegrityError` o error de validación ante códigos duplicados.
- `test_precio_no_negativo`: Valida que no se permitan precios inferiores a cero.
- `test_calculo_reporte_stock_critico`: Comprueba la precisión del filtrado analítico.
