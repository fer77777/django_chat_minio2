from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from productos.models import Producto, CategoriaChocolate


class Command(BaseCommand):
    help = 'Pobla el inventario con chocolates iniciales de prueba con datos realistas'

    def handle(self, *args, **kwargs):
        chocolates = [
            {
                'codigo': 'CHOC-001',
                'nombre': 'Barra Silvestre Alto Beni 85%',
                'descripcion': 'Chocolate negro amargo de origen silvestre con notas a frutos rojos y madera noble.',
                'categoria': CategoriaChocolate.NEGRO,
                'precio': Decimal('35.00'),
                'cantidad_existente': 25,
                'porcentaje_cacao': 85,
                'origen_cacao': 'Alto Beni, La Paz, Bolivia',
                'estado': True,
            },
            {
                'codigo': 'CHOC-002',
                'nombre': 'Bombones Rellenos de Maracuyá',
                'descripcion': 'Caja de 6 bombones finos rellenos de ganache de maracuyá amazónico.',
                'categoria': CategoriaChocolate.RELLENO,
                'precio': Decimal('48.00'),
                'cantidad_existente': 8,  # Stock crítico para probar reportes
                'porcentaje_cacao': 60,
                'origen_cacao': 'Chapare, Cochabamba, Bolivia',
                'estado': True,
            },
            {
                'codigo': 'CHOC-003',
                'nombre': 'Chocolate con Leche & Almendras Chiquitanas',
                'descripcion': 'Cremoso chocolate con leche enriquecido con almendras tostadas de la Chiquitanía.',
                'categoria': CategoriaChocolate.LECHE,
                'precio': Decimal('28.50'),
                'cantidad_existente': 42,
                'porcentaje_cacao': 45,
                'origen_cacao': 'Santa Cruz, Bolivia',
                'estado': True,
            },
            {
                'codigo': 'CHOC-004',
                'nombre': 'Trufas Artesanales al Café Yungueño',
                'descripcion': 'Trufas cubiertas de polvo de cacao fino rellenas de infusión de café arábica.',
                'categoria': CategoriaChocolate.TRUFAS,
                'precio': Decimal('55.00'),
                'cantidad_existente': 5,  # Stock crítico
                'porcentaje_cacao': 70,
                'origen_cacao': 'Caranavi, La Paz, Bolivia',
                'estado': True,
            },
            {
                'codigo': 'CHOC-005',
                'nombre': 'Barra Chocolate Blanco con Sal Rosada de Uyuni',
                'descripcion': 'Manteca de cacao pura infusionada con vainilla y escamas de sal del Salar de Uyuni.',
                'categoria': CategoriaChocolate.BLANCO,
                'precio': Decimal('32.00'),
                'cantidad_existente': 18,
                'porcentaje_cacao': 35,
                'origen_cacao': 'Beni, Bolivia',
                'estado': True,
            },
            {
                'codigo': 'CHOC-006',
                'nombre': 'Edición Especial Cacao Criollo 90% Ancestral',
                'descripcion': 'Lote de edición limitada elaborado con cacao criollo recolectado a mano.',
                'categoria': CategoriaChocolate.ESPECIAL,
                'precio': Decimal('65.00'),
                'cantidad_existente': 12,
                'porcentaje_cacao': 90,
                'origen_cacao': 'Madidi, Bolivia',
                'estado': True,
            },
            {
                'codigo': 'CHOC-007',
                'nombre': 'Bombón de Licor de Singani (Lote Anterior)',
                'descripcion': 'Lote anterior en prueba de cata, actualmente descontinuado temporalmente.',
                'categoria': CategoriaChocolate.RELLENO,
                'precio': Decimal('40.00'),
                'cantidad_existente': 0,
                'porcentaje_cacao': 55,
                'origen_cacao': 'Tarija / La Paz, Bolivia',
                'estado': False,  # Inactivo
            },
        ]

        creados = 0
        for data in chocolates:
            obj, created = Producto.objects.update_or_create(
                codigo=data['codigo'],
                defaults=data
            )
            if created:
                creados += 1

        self.stdout.write(self.style.SUCCESS(f'¡Listo! Se registraron/actualizaron {len(chocolates)} chocolates de prueba ({creados} nuevos).'))
