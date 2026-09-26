# Entregable Final - Programación 4: Sistema de Chocolatería con CRUD y Reportes

## 1. Descripción General del Proyecto

Se ha desarrollado e integrado un sistema completo de administración de inventarios y catálogo para una **Chocolatería Artesanal Gourmet**, cumpliendo de forma estricta con todas las especificaciones y lineamientos establecidos en el documento de requerimientos de la materia.

La aplicación permite la gestión integral de productos a través de operaciones **CRUD** (Crear, Leer/Consultar, Actualizar y Eliminar), control de stock físico, alertas de inventario crítico y un módulo analítico de reportes predefinidos.

---

## 2. Modelo de Datos (`Producto`)

El modelo `Producto` se encuentra en `productos/models.py` y cuenta con los 9 campos obligatorios solicitados:

| N° | Campo | Tipo en Django | Restricción / Validación | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `codigo` | `CharField(max_length=50)` | `unique=True` (Obligatorio) | Identificador único del chocolate (ej. `CHOC-001`). |
| 2 | `nombre` | `CharField(max_length=150)` | Obligatorio | Nombre comercial del producto artesanal. |
| 3 | `descripcion` | `TextField` | Opcional (`blank=True, null=True`) | Notas de cata, perfil sensorial y detalles del producto. |
| 4 | `categoria` | `CharField(choices=...)` | Obligatorio con opciones | Negro/Amargo, Con Leche, Blanco, Relleno/Bombón, Trufas, Gourmet. |
| 5 | `precio` | `DecimalField` | `validators=[MinValueValidator(0.0)]` | Precio unitario no negativo en Bolivianos (Bs.). |
| 6 | `cantidad_existente` | `PositiveIntegerField` | `validators=[MinValueValidator(0)]` | Unidades físicas disponibles en depósito. |
| 7 | `estado` | `BooleanField` | Obligatorio (Default: `True`) | Estado activo o inactivo (descontinuado) para la venta. |
| 8 | `fecha_ingreso` | `DateField` | Obligatorio (Default: `timezone.now`) | Fecha de registro del lote en el inventario. |
| 9 | `imagen` | `ImageField(upload_to='productos/')` | Opcional | Fotografía del producto almacenada en `media/productos/`. |

### Campos Especiales del Rubro (Chocolatería):
- `porcentaje_cacao`: `PositiveIntegerField` con rango 0-100% de pureza de grano.
- `origen_cacao`: `CharField` especificando la región de procedencia (ej. Alto Beni, Madidi, Chapare).

---

## 3. Funcionalidades del Módulo CRUD

1. **Catálogo Principal (`/productos/`)**:
   - Vista en cuadrícula responsive de chocolates con tarjetas visuales.
   - Filtro interactivo por **categoría** de chocolate.
   - Buscador por **nombre** y **código**.
   - Filtro por **estado** (Activo / Inactivo).
   - Indicadores visuales para productos con **stock crítico** (< 10 unidades).

2. **Registro de Producto (`/productos/crear/`)**:
   - Formulario validado con Django Forms.
   - Validación de precios no negativos y cantidades enteras válidas.
   - Carga y procesamiento de imágenes.

3. **Ficha de Detalle (`/productos/<id>/`)**:
   - Muestra las especificaciones técnicas completas del chocolate, porcentaje de pureza de cacao, origen y valoración total del lote.

4. **Modificación (`/productos/<id>/editar/`)**:
   - Actualización de cualquier campo del producto con persistencia inmediata.

5. **Eliminación (`/productos/<id>/eliminar/`)**:
   - Pantalla de confirmación para evitar eliminaciones accidentales.

---

## 4. Módulo de Reportes Analíticos (`/productos/reportes/`)

Cumpliendo con la sección de reportes predefinidos del documento:
- **Alerta de Stock Crítico**: Tabla automática que lista todos los chocolates con menos de 10 unidades para reabastecimiento.
- **Distribución por Categorías**: Cálculo dinámico del total de piezas y el valor monetario acumulado por cada tipo de chocolate.
- **Línea Gourmet de Alta Pureza**: Filtrado de productos con 70% o más de cacao puro.
- **Métricas Globales**: Total de capital invertido en mercadería (Bs.), total de unidades físicas y precio promedio ponderado.
- **Top 5 Productos Exclusivos**: Los productos con mayor precio unitario de la tienda.

---

## 5. Estructura de Directorios Incorporada

```text
django_chat/
│
├── media/
│   └── productos/                <-- Almacenamiento de imágenes de chocolates subidas
├── static/
│   ├── css/                      <-- Estilos de la aplicación
│   └── images/                   <-- Íconos y logotipos
├── productos/                    <-- Aplicación Django de Chocolatería
│   ├── management/commands/      <-- Script 'poblar_chocolates.py' para datos de prueba
│   ├── forms.py                  <-- Validaciones de entrada
│   ├── models.py                 <-- Modelo de 9 campos + atributos de cacao
│   ├── urls.py                   <-- Enrutamiento del módulo
│   └── views.py                  <-- Lógica CRUD y generación de reportes
└── templates/
    └── productos/                <-- Plantillas HTML con diseño artesanal moderno
        ├── lista.html
        ├── detalle.html
        ├── formulario.html
        ├── eliminar_confirmar.html
        └── reportes.html
```

---

## 6. Comando para Poblar Datos Iniciales

Para cargar los 7 chocolates iniciales con stock, categorías y pureza de cacao de prueba:
```powershell
.\.venv\Scripts\python.exe manage.py poblar_chocolates
```
