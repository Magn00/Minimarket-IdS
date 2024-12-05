from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, HistorialEstadoPedido, Usuario, HistorialCambioRol
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import cm
from django.http import HttpResponse
from .forms import ProductoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required


from django import forms
from .models import Pedido, DetallePedido, HistorialCambioRol








from django.contrib.auth import login
from .forms import RegistroForm


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente después del registro
            return redirect('lista_productos')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})













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

# Vista para que el vendedor agregue o edite productos
@login_required
@role_required('administrador')
def agregar_modificar_producto(request, producto_id=None):
    producto = get_object_or_404(Producto, id=producto_id) if producto_id else None
    nombre_producto = None  # Inicializamos el nombre del producto
    productos = Producto.objects.all()  # Obtener todos los productos

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()  # Guardamos el producto
            nombre_producto = producto.nombre  # Obtenemos el nombre del producto guardado
            if producto_id:
                messages.success(request, f'¡El producto "{nombre_producto}" ha sido modificado exitosamente!')
            else:
                messages.success(request, f'¡El producto "{nombre_producto}" ha sido agregado exitosamente!')
            return redirect('agregar_producto')  # Redirigimos después de guardar
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'core/agregar_modificar_producto.html', {
        'form': form,
        'productos': productos,  # Pasamos la lista de productos
        'producto': producto,  # Pasamos el producto actual (None si es agregar)
    })


#Borrar producto
@login_required
@role_required('administrador')
def borrar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    nombre_producto = producto.nombre  # Guardamos el nombre antes de eliminarlo
    producto.delete()  # Eliminamos el producto
    messages.success(request, f'¡El producto "{nombre_producto}" ha sido eliminado exitosamente!')
    return redirect('agregar_producto')  # Redirigimos de nuevo a la vista de agregar/modificar

# Generar el pdf

def generar_pdf_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pedido_{pedido_id}.pdf"'
    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    elementos = []
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'Titulo',
        parent=estilos['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=1,  # Centrado
        spaceAfter=20
    )
    estilo_normal_bold = ParagraphStyle(
        'NormalBold',
        parent=estilos['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        spaceAfter=5
    )
    estilo_normal = ParagraphStyle(
        'Normal',
        parent=estilos['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    elementos.append(Paragraph('Detalle del Pedido', estilo_titulo))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f'<b>Pedido N°:</b> {pedido.id}', estilo_normal))
    elementos.append(Paragraph(f'<b>Cliente:</b> {pedido.nombre_cliente}', estilo_normal))
    elementos.append(Paragraph(f'<b>Dirección de envío:</b> {pedido.direccion_envio}', estilo_normal))
    elementos.append(Paragraph(f'<b>Correo electrónico:</b> {pedido.correo_electronico}', estilo_normal))
    elementos.append(Paragraph(f'<b>Fecha de pedido:</b> {pedido.fecha_pedido.strftime("%d/%m/%Y %H:%M")}', estilo_normal))
    elementos.append(Paragraph(f'<b>Total:</b> ${pedido.total:.2f}', estilo_normal))
    elementos.append(Spacer(1, 12))
    datos = [['Producto', 'Cantidad', 'Precio Unitario', 'Total']]
    for detalle in detalles:
        producto = detalle.producto
        cantidad = detalle.cantidad
        precio_unitario = producto.precio
        total_producto = cantidad * precio_unitario
        datos.append([
            producto.nombre,
            cantidad,
            f"${precio_unitario:.2f}",
            f"${total_producto:.2f}"
        ])
    tabla = Table(datos, colWidths=[8*cm, 3*cm, 4*cm, 4*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),  # Fondo azul en encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),              # Texto blanco en encabezado
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#D9E1F2")),  # Fondo azul claro en filas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    for i in range(1, len(datos)):
        if i % 2 == 0:
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.HexColor("#F2F2F2")),
            ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 24))
    elementos.append(Paragraph(f'<b>Total a Pagar:</b> ${pedido.total:.2f}', estilo_normal_bold))
    elementos.append(Spacer(1, 12))
    footer_text = "Gracias por tu compra. Si tienes alguna pregunta, no dudes en contactarnos."
    elementos.append(Paragraph(footer_text, estilo_normal))
    
    doc.build(elementos)

    return response

def lista_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')  # Ordenar por fecha más reciente primero
    return render(request, 'core/lista_pedidos.html', {'pedidos': pedidos})

def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'core/detalle_pedido.html', {'pedido': pedido})   

@login_required
@role_required('administrador')
def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADOS).keys() and nuevo_estado != pedido.estado:
            # Crear un registro en el historial de cambio
            HistorialEstadoPedido.objects.create(
                pedido=pedido,
                estado_anterior=pedido.estado,
                estado_nuevo=nuevo_estado,
                usuario=request.user  # Registrar el usuario que hace el cambio
            )
            # Actualizar el estado del pedido
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f"El estado del pedido {pedido.id} ha sido actualizado a {pedido.get_estado_display()}.")
        else:
            messages.error(request, "El estado seleccionado es inválido o no hay cambios.")
    
    return render(request, 'core/cambiar_estado_pedido.html', {'pedido': pedido})   
@login_required
@role_required('administrador')
def cambiar_rol_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        if nuevo_rol != usuario.rol:
            HistorialCambioRol.objects.create(
                usuario_modificado=usuario,
                rol_anterior=usuario.rol,
                rol_nuevo=nuevo_rol,
                usuario_modificador=request.user
            )
            usuario.rol = nuevo_rol
            usuario.save()
            messages.success(request, f"El rol de {usuario.nombre} ha sido cambiado a {nuevo_rol}.")
        else:
            messages.warning(request, "El nuevo rol debe ser diferente al actual.")
    return redirect('lista_usuarios')

@login_required
@role_required('administrador')
def historial_cambios_roles(request):

    historial = HistorialCambioRol.objects.all().order_by('-fecha_cambio')
    return render(request, 'core/historial_cambios_roles.html', {'historial': historial})


def error_403(request, exception=None):
    return render(request, 'core/403.html', status=403)