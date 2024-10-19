from django.contrib import admin
from .models import Producto, Pedido, DetallePedido

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'stock')  # Mostrar ID junto al nombre
    search_fields = ('nombre',)

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('nombre_cliente', 'fecha_pedido', 'total')
    inlines = [DetallePedidoInline]

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)