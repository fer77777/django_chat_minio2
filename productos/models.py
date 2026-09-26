from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class CategoriaChocolate(models.TextChoices):
    NEGRO = 'Negro / Amargo', 'Negro / Amargo (70%+ Cacao)'
    LECHE = 'Con Leche', 'Chocolate con Leche'
    BLANCO = 'Blanco', 'Chocolate Blanco'
    RELLENO = 'Relleno / Bombón', 'Bombones y Rellenos'
    TRUFAS = 'Trufas', 'Trufas Artesanales'
    ESPECIAL = 'Edición Especial', 'Edición Especial / Gourmet'


class Producto(models.Model):
    """
    Modelo de Producto (Chocolatería Artesanal).
    Cumple con los 9 campos obligatorios del documento de Programación 4:
    1. codigo (único, obligatorio)
    2. nombre (obligatorio)
    3. descripcion (opcional)
    4. categoria (obligatorio)
    5. precio (decimal, >= 0, obligatorio)
    6. cantidad_existente (entero, >= 0, obligatorio)
    7. estado (activo / inactivo, obligatorio)
    8. fecha_ingreso (fecha registro, obligatorio)
    9. imagen (archivo multimedia opcional para la tienda)
    + Campos específicos de chocolatería complementarios:
    - porcentaje_cacao (0-100%)
    - origen_cacao
    """
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código del Producto",
        help_text="Código único identificador (ej: CHOC-001)"
    )
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre del Chocolate",
        help_text="Nombre comercial del producto"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Detalles del chocolate, notas de cata o ingredientes"
    )
    categoria = models.CharField(
        max_length=50,
        choices=CategoriaChocolate.choices,
        default=CategoriaChocolate.NEGRO,
        verbose_name="Categoría"
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        verbose_name="Precio (Bs.)",
        help_text="Precio unitario en Bolivianos"
    )
    cantidad_existente = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Cantidad en Stock",
        help_text="Unidades físicas disponibles"
    )
    estado = models.BooleanField(
        default=True,
        verbose_name="Estado Activo",
        help_text="Indica si el producto está disponible para la venta"
    )
    fecha_ingreso = models.DateField(
        default=timezone.now,
        verbose_name="Fecha de Ingreso",
        help_text="Fecha en que ingresó al inventario"
    )
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        verbose_name="Fotografía del Producto"
    )
    
    # Atributos de chocolatería gourmet
    porcentaje_cacao = models.PositiveIntegerField(
        default=70,
        blank=True,
        null=True,
        verbose_name="% de Cacao",
        help_text="Porcentaje de pureza de cacao (0 a 100)"
    )
    origen_cacao = models.CharField(
        max_length=100,
        blank=True,
        default="Alto Beni, Bolivia",
        verbose_name="Origen del Cacao"
    )

    class Meta:
        verbose_name = "Producto de Chocolatería"
        verbose_name_plural = "Productos de Chocolatería"
        ordering = ['-fecha_ingreso', 'nombre']

    def __str__(self):
        return f"[{self.codigo}] {self.nombre} - Bs. {self.precio}"

    @property
    def stock_bajo(self):
        """Retorna True si el stock es crítico (menor a 10 unidades)."""
        return self.cantidad_existente < 10

    @property
    def valor_total_inventario(self):
        """Calcula el valor monetario total de este lote."""
        return self.precio * self.cantidad_existente
