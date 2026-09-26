from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Avg, Count, Max, Min, F
from .models import Producto, CategoriaChocolate
from .forms import ProductoForm


def producto_lista(request):
    """
    Listado principal de productos con filtros por categoría, búsqueda y estado.
    """
    categoria_filtro = request.GET.get('categoria', '')
    busqueda = request.GET.get('q', '')
    estado_filtro = request.GET.get('estado', '')

    productos = Producto.objects.all()

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda) | productos.filter(codigo__icontains=busqueda)

    if categoria_filtro:
        productos = productos.filter(categoria=categoria_filtro)

    if estado_filtro != '':
        if estado_filtro.lower() in ['1', 'true', 'activo']:
            productos = productos.filter(estado=True)
        elif estado_filtro.lower() in ['0', 'false', 'inactivo']:
            productos = productos.filter(estado=False)

    # Resumen rápido de métricas de chocolatería
    total_unidades = productos.aggregate(total=Sum('cantidad_existente'))['total'] or 0
    total_variedades = productos.count()
    bajo_stock_count = productos.filter(cantidad_existente__lt=10).count()

    context = {
        'productos': productos,
        'categorias': CategoriaChocolate.choices,
        'categoria_filtro': categoria_filtro,
        'busqueda': busqueda,
        'estado_filtro': estado_filtro,
        'total_unidades': total_unidades,
        'total_variedades': total_variedades,
        'bajo_stock_count': bajo_stock_count,
    }
    return render(request, 'productos/lista.html', context)


def producto_detalle(request, pk):
    """Ver detalles completos de un chocolate."""
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'productos/detalle.html', {'producto': producto})


def producto_crear(request):
    """Crear nuevo chocolate en el catálogo."""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_prod = form.save()
            messages.success(request, f'¡Chocolate "{nuevo_prod.nombre}" registrado exitosamente!')
            return redirect('productos:lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = ProductoForm()

    return render(request, 'productos/formulario.html', {
        'form': form,
        'titulo': 'Nuevo Chocolate Artesanal',
        'boton_texto': 'Registrar Chocolate'
    })


def producto_editar(request, pk):
    """Editar un chocolate existente."""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Chocolate "{producto.nombre}" actualizado con éxito!')
            return redirect('productos:detalle', pk=producto.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'productos/formulario.html', {
        'form': form,
        'producto': producto,
        'titulo': f'Editar: {producto.nombre}',
        'boton_texto': 'Guardar Cambios'
    })


def producto_eliminar(request, pk):
    """Eliminar chocolate del inventario."""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'El chocolate "{nombre}" fue eliminado del catálogo.')
        return redirect('productos:lista')

    return render(request, 'productos/eliminar_confirmar.html', {'producto': producto})


# ========================================================
# REPORTES PREDEFINIDOS REQUERIDOS POR EL DOCUMENTO
# ========================================================

def reportes_panel(request):
    """
    Vista central de reportes analíticos de inventario:
    1. Productos con stock crítico (< 10 unidades)
    2. Productos más caros y más económicos
    3. Distribución por categorías y valoración monetaria total
    4. Productos inactivos / descontinuados
    5. Chocolates de alta pureza (>= 70% Cacao)
    """
    # 1. Stock crítico
    stock_critico = Producto.objects.filter(cantidad_existente__lt=10).order_by('cantidad_existente')
    
    # 2. Productos activos vs inactivos
    total_activos = Producto.objects.filter(estado=True).count()
    total_inactivos = Producto.objects.filter(estado=False).count()
    
    # 3. Métricas de precios
    stats_precio = Producto.objects.aggregate(
        precio_max=Max('precio'),
        precio_min=Min('precio'),
        precio_promedio=Avg('precio')
    )
    chocolates_top_precio = Producto.objects.order_by('-precio')[:5]
    
    # 4. Pureza de Cacao Gourmet (>= 70%)
    alta_pureza = Producto.objects.filter(porcentaje_cacao__gte=70).order_by('-porcentaje_cacao')

    # 5. Valoración por categoría
    categorias_stats = []
    for cat_val, cat_label in CategoriaChocolate.choices:
        prods = Producto.objects.filter(categoria=cat_val)
        count = prods.count()
        if count > 0:
            total_stock = prods.aggregate(s=Sum('cantidad_existente'))['s'] or 0
            # Valor total = sum(precio * cantidad)
            valor_inventario = sum(p.precio * p.cantidad_existente for p in prods)
            categorias_stats.append({
                'nombre': cat_label,
                'cantidad_variedades': count,
                'total_unidades': total_stock,
                'valor_total': valor_inventario,
            })

    # Valor total global del inventario
    todos_los_productos = Producto.objects.all()
    valor_global = sum(p.precio * p.cantidad_existente for p in todos_los_productos)
    total_piezas_global = sum(p.cantidad_existente for p in todos_los_productos)

    context = {
        'stock_critico': stock_critico,
        'total_activos': total_activos,
        'total_inactivos': total_inactivos,
        'stats_precio': stats_precio,
        'chocolates_top_precio': chocolates_top_precio,
        'alta_pureza': alta_pureza,
        'categorias_stats': categorias_stats,
        'valor_global': valor_global,
        'total_piezas_global': total_piezas_global,
    }
    return render(request, 'productos/reportes.html', context)
