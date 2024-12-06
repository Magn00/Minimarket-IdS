from itertools import groupby
from operator import itemgetter

def enviar_notificaciones():
    print("Ejecutando enviar_notificaciones...")
    productos_bajo_stock = Producto.objects.filter(stock__lt=10).order_by("categoria")  # Agrupa por categoría
    if productos_bajo_stock.exists():
        mensaje = "Los siguientes productos tienen bajo stock:\n"

        # Agrupar por categorías
        for categoria, items in groupby(productos_bajo_stock, key=lambda x: x.categoria):
            mensaje += f"\nCategoría: {categoria}\n"
            for producto in items:
                mensaje += f"- {producto.nombre}: {producto.stock} unidades disponibles.\n"

        # Sugerir reposición
        mensaje += "\nSugerencia de reposición:\n"
        for categoria, items in groupby(productos_bajo_stock, key=lambda x: x.categoria):
            mensaje += f"\nCategoría: {categoria}\n"
            for producto in items:
                cantidad_reponer = 20 - producto.stock
                mensaje += f"- {producto.nombre}: Reponer {cantidad_reponer} unidades.\n"

        # Enviar correo
        send_mail(
            subject="Notificación: Productos con bajo stock",
            message=mensaje,
            from_email="arlette.carvajal@sansano.usm.cl",
            recipient_list=["arlette.carvajal@sansano.usm.cl"],
            fail_silently=False,
        )
        print("Correo enviado con éxito.")
    else:
        print("No hay productos con bajo stock.")
