from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"[ID: {self.id}] {self.nombre}"

class Pedido(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    direccion_envio = models.CharField(max_length=255)
    correo_electronico = models.EmailField()
    productos = models.ManyToManyField(Producto, through='DetallePedido')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.nombre_cliente}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} - Cantidad: {self.cantidad}"