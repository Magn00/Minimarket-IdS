from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto





from django import forms
from .models import Pedido, DetallePedido

# Formulario para los datos del pedido
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'direccion_envio', 'correo_electronico']

# Vista para el checkout
def checkout(request):
    carrito = request.session.get('carrito', {})
    total_carrito = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.total = total_carrito
            pedido.save()

            # Guardar productos del carrito en DetallePedido
            for producto_id, detalles in carrito.items():
                producto = Producto.objects.get(id=producto_id)
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=detalles['cantidad']
                )

            # Limpiar el carrito después de realizar el pedido
            del request.session['carrito']
            return redirect('lista_productos')  # Puedes redirigir a una página de éxito si prefieres
    else:
        form = PedidoForm()

    return render(request, 'core/checkout.html', {'form': form, 'total_carrito': total_carrito})









# Vista para mostrar los productos disponibles
def lista_productos(request):
    productos = Producto.objects.all()  # Obtenemos todos los productos
    return render(request, 'core/lista_productos.html', {'productos': productos})

# Función auxiliar para obtener el carrito
def obtener_carrito(request):
    carrito = request.session.get('carrito', {})
    return carrito

# Función auxiliar para guardar el carrito en la sesión
def guardar_carrito(request, carrito):
    request.session['carrito'] = carrito

# Añadir producto al carrito
def agregar_al_carrito(request, producto_id):
    carrito = obtener_carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)

    # Añadir o actualizar la cantidad del producto en el carrito
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': str(producto.precio),  # Almacenamos el precio como string por si hay decimales
            'cantidad': 1,
        }

    guardar_carrito(request, carrito)  # Guardamos el carrito en la sesión
    return redirect('lista_productos')

# Vista para mostrar el carrito
def ver_carrito(request):
    carrito = obtener_carrito(request)

    # Calcular el total del carrito y total por producto
    total_carrito = 0
    for item_id, item in carrito.items():
        item['total_producto'] = float(item['precio']) * item['cantidad']  # Total por producto
        total_carrito += item['total_producto']  # Sumamos al total general

    return render(request, 'core/ver_carrito.html', {'carrito': carrito, 'total_carrito': total_carrito})

# Eliminar producto del carrito
def eliminar_del_carrito(request, producto_id):
    carrito = obtener_carrito(request)

    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        guardar_carrito(request, carrito)  # Actualizamos el carrito en la sesión

    return redirect('ver_carrito')
