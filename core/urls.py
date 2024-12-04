from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import generar_pdf_pedido

from django.contrib.auth.views import LoginView, LogoutView
from .views import registro

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedido/<int:pedido_id>/pdf/', generar_pdf_pedido, name='generar_pdf_pedido'),
    path('agregar_producto/', views.agregar_modificar_producto, name='agregar_producto'),
    path('modificar_producto/<int:producto_id>/', views.agregar_modificar_producto, name='modificar_producto'),
    path('borrar_producto/<int:producto_id>/', views.borrar_producto, name='borrar_producto'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedido/<int:pedido_id>/cambiar_estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('registro/', registro, name='registro'),
    path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)