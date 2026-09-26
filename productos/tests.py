from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from .models import Producto, CategoriaChocolate


class ProductoModelTests(TestCase):
    """Pruebas unitarias para validar las reglas del modelo Producto (RF-01 a RF-05)."""

    def setUp(self):
        self.prod1 = Producto.objects.create(
            codigo="CHOC-TEST-001",
            nombre="Chocolate Amargo 70%",
            categoria=CategoriaChocolate.NEGRO,
            precio=Decimal("35.50"),
            cantidad_existente=15,
            porcentaje_cacao=70,
            origen_cacao="Alto Beni",
            estado=True
        )

    def test_creacion_producto_exitosa(self):
        """Verifica que un producto con datos válidos se cree correctamente."""
        self.assertEqual(self.prod1.codigo, "CHOC-TEST-001")
        self.assertEqual(self.prod1.nombre, "Chocolate Amargo 70%")
        self.assertEqual(self.prod1.precio, Decimal("35.50"))
        self.assertEqual(self.prod1.cantidad_existente, 15)
        self.assertTrue(self.prod1.estado)

    def test_validacion_codigo_unico(self):
        """Verifica que no se permita registrar dos productos con el mismo código (RF-01, RF-03)."""
        with self.assertRaises(IntegrityError):
            Producto.objects.create(
                codigo="CHOC-TEST-001",  # Código duplicado
                nombre="Chocolate Blanco Duplicado",
                categoria=CategoriaChocolate.BLANCO,
                precio=Decimal("20.00"),
                cantidad_existente=5
            )

    def test_validacion_precio_no_negativo(self):
        """Verifica que el precio no pueda ser un valor negativo (RF-03)."""
        prod_invalido = Producto(
            codigo="CHOC-NEG-001",
            nombre="Chocolate Precio Negativo",
            categoria=CategoriaChocolate.LECHE,
            precio=Decimal("-10.00"),
            cantidad_existente=5
        )
        with self.assertRaises(ValidationError):
            prod_invalido.full_clean()

    def test_validacion_cantidad_existente_no_negativa(self):
        """Verifica que el stock no pueda ser menor a cero (RF-03, RF-05)."""
        prod_invalido = Producto(
            codigo="CHOC-NEG-002",
            nombre="Chocolate Stock Negativo",
            categoria=CategoriaChocolate.RELLENO,
            precio=Decimal("15.00"),
            cantidad_existente=-5
        )
        with self.assertRaises(ValidationError):
            prod_invalido.full_clean()

    def test_calculo_valor_total_inventario(self):
        """Verifica que la propiedad valor_total_inventario calcule precio * cantidad_existente."""
        # 35.50 * 15 = 532.50
        esperado = Decimal("35.50") * 15
        self.assertEqual(self.prod1.valor_total_inventario, esperado)

    def test_deteccion_stock_bajo(self):
        """Verifica que se active stock_bajo si hay menos de 10 unidades."""
        self.assertFalse(self.prod1.stock_bajo)  # Tiene 15 unidades

        prod_critico = Producto.objects.create(
            codigo="CHOC-CRIT-001",
            nombre="Trufa Crítica",
            categoria=CategoriaChocolate.TRUFAS,
            precio=Decimal("12.00"),
            cantidad_existente=4  # < 10 unidades
        )
        self.assertTrue(prod_critico.stock_bajo)


class ReportesCalculoTests(TestCase):
    """Pruebas unitarias para validar las métricas y cálculos de los reportes (RF-06)."""

    def setUp(self):
        Producto.objects.create(
            codigo="CHOC-A", nombre="Barra Económica", categoria=CategoriaChocolate.LECHE,
            precio=Decimal("10.00"), cantidad_existente=20, estado=True
        )
        Producto.objects.create(
            codigo="CHOC-B", nombre="Edición Especial Cara", categoria=CategoriaChocolate.ESPECIAL,
            precio=Decimal("80.00"), cantidad_existente=5, estado=True
        )
        Producto.objects.create(
            codigo="CHOC-C", nombre="Bombón Agotado", categoria=CategoriaChocolate.RELLENO,
            precio=Decimal("25.00"), cantidad_existente=0, estado=False
        )

    def test_identificacion_producto_mas_caro_y_mas_barato(self):
        """Verifica la correcta obtención del producto de mayor y menor precio."""
        mas_caro = Producto.objects.order_by('-precio').first()
        mas_barato = Producto.objects.order_by('precio').first()

        self.assertEqual(mas_caro.codigo, "CHOC-B")
        self.assertEqual(mas_caro.precio, Decimal("80.00"))

        self.assertEqual(mas_barato.codigo, "CHOC-A")
        self.assertEqual(mas_barato.precio, Decimal("10.00"))

    def test_consulta_productos_agotados(self):
        """Verifica que se listen correctamente los productos con stock 0."""
        agotados = Producto.objects.filter(cantidad_existente=0)
        self.assertEqual(agotados.count(), 1)
        self.assertEqual(agotados.first().codigo, "CHOC-C")

    def test_calculo_valor_total_inventario_global(self):
        """Verifica el cálculo de valoración monetaria de todo el inventario."""
        # CHOC-A: 10 * 20 = 200
        # CHOC-B: 80 * 5  = 400
        # CHOC-C: 25 * 0  = 0
        # Total = 600.00
        todos = Producto.objects.all()
        total_calculado = sum(p.precio * p.cantidad_existente for p in todos)
        self.assertEqual(total_calculado, Decimal("600.00"))
