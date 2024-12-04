from django.conf import settings
from django.db import models



from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    PREGUNTAS_RECUPERACION = [
        ('1', '¿Cuál es el nombre de tu primera mascota?'),
        ('2', '¿Cuál es tu comida favorita?'),
        ('3', '¿Cuál es el nombre de tu mejor amigo de la infancia?'),
    ]

    nombre = models.CharField(max_length=150)
    correo = models.EmailField(unique=True)
    pregunta_recuperacion = models.CharField(max_length=1, choices=PREGUNTAS_RECUPERACION)
    respuesta_pregunta = models.CharField(max_length=150)
    rol = models.CharField(max_length=50, choices=[('cliente', 'Cliente'), ('trabajador', 'Trabajador')])

    # Hacer que el 'username' sea igual al 'correo' si no se proporciona
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.correo  # Usa 'correo' como 'username' si no se proporciona
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.rol})"

    # Configuración para usar 'correo' como campo de autenticación
    USERNAME_FIELD = 'correo'  # Usa 'correo' para autenticación
    REQUIRED_FIELDS = ['username', 'nombre', 'rol']  # 'username' sigue siendo obligatorio

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"[ID: {self.id}] {self.nombre}"

class Pedido(models.Model):
    ESTADOS = [
        ('PRE', 'Preparación'),
        ('TRA', 'En tránsito'),
        ('ENT', 'Entregado'),
        ('CAN', 'Cancelado'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=100)
    direccion_envio = models.CharField(max_length=255)
    correo_electronico = models.EmailField()
    productos = models.ManyToManyField('Producto', through='DetallePedido')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=3, choices=ESTADOS, default='PRE')  # Campo de estado

    def __str__(self):
        return f"Pedido {self.id} - {self.nombre_cliente} - Estado: {self.get_estado_display()}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} - Cantidad: {self.cantidad}"
    
class HistorialEstadoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='historial_estados')
    estado_anterior = models.CharField(max_length=3, choices=Pedido.ESTADOS)
    estado_nuevo = models.CharField(max_length=3, choices=Pedido.ESTADOS)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)  # Actualizado

    def __str__(self):
        return f"Historial Pedido {self.pedido.id} - {self.get_estado_anterior_display()} a {self.get_estado_nuevo_display()} por {self.usuario}"