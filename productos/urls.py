from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.producto_lista, name='lista'),
    path('crear/', views.producto_crear, name='crear'),
    path('<int:pk>/', views.producto_detalle, name='detalle'),
    path('<int:pk>/editar/', views.producto_editar, name='editar'),
    path('<int:pk>/eliminar/', views.producto_eliminar, name='eliminar'),
    path('reportes/', views.reportes_panel, name='reportes'),
]
