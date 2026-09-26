from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio', 'cantidad_existente', 'porcentaje_cacao', 'estado', 'fecha_ingreso')
    list_filter = ('categoria', 'estado', 'fecha_ingreso')
    search_fields = ('codigo', 'nombre', 'descripcion', 'origen_cacao')
    list_editable = ('precio', 'cantidad_existente', 'estado')
    ordering = ('-fecha_ingreso',)
