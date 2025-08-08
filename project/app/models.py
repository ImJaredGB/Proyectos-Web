from django.db import models

# Tabla base de Usuarios
class Usuario(models.Model):
    TIPOS = (
        ('admin', 'Administrador'),
        ('residente', 'Residente'),
    )

    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    tipe = models.CharField(max_length=10, choices=TIPOS)

    def __str__(self):
        return self.username

# Administrador
class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rol = models.CharField(max_length=50)
    permisos = models.TextField()

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Habitación
class Habitacion(models.Model):
    ZONAS = [
        ('Castillo', 'Castillo'),
        ('Restaurante', 'Restaurante'),
        ('Piso', 'Piso'),
        ('Vilanova', 'Vilanova'),
    ]
    nomenclatura = models.CharField(max_length=10, unique=True)
    estado = models.BooleanField(default=True)
    tamaño = models.PositiveIntegerField()
    zona = models.CharField(max_length=20, choices=ZONAS)
    desactivada = models.BooleanField(default=False)

    def __str__(self):
        return self.nomenclatura

# Litera
class Litera(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    estado = models.BooleanField(default=True)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, related_name='literas')

    def __str__(self):
        return self.codigo

# Residente
class Residente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    n_documento = models.CharField(max_length=50)
    llegada = models.DateField(null=True, blank=True)
    salida = models.DateField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    estado = models.CharField(max_length=50, null=True, blank=True)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='residentes')
    litera = models.ForeignKey(Litera, on_delete=models.SET_NULL, null=True, blank=True, related_name='ocupantes')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"