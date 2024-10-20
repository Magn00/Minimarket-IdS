from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),  # Listar productos
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),  # Añadir producto al carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),  # Ver carrito
    path('eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),  # Eliminar del carrito
    path('checkout/', views.checkout, name='checkout'),  # Proceso de checkout
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)