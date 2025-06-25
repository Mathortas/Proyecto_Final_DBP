from django.db import models
from django.contrib.auth.models import User as Usuario


class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ciclo = models.CharField(max_length=20)
    modalidad = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    creditos = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'curso'


class Horario(models.Model):
    id_horario = models.AutoField(primary_key=True)
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE, db_column='id_curso')
    dia_semana = models.CharField(max_length=20)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'horario'


class Matricula(models.Model):
    id_matricula = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE, db_column='id_curso')
    ciclo = models.CharField(max_length=20)
    fecha_matricula = models.DateField()

    class Meta:
        managed = True
        db_table = 'matricula'


class Nota(models.Model):
    id_nota = models.AutoField(primary_key=True)
    nombre_nota = models.CharField(max_length=100)
    nota_obtenida = models.DecimalField(max_digits=5, decimal_places=2)
    peso_porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    id_matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, db_column='id_matricula')

    class Meta:
        managed = True
        db_table = 'nota'
    def __str__(self):
        return f"{self.nombre_nota} - {self.nota_obtenida} ({self.peso_porcentaje}%)"

class Tarea(models.Model):
    id_tarea = models.AutoField(primary_key=True)
    nombre_tarea = models.CharField(max_length=100)
    fecha_entrega = models.DateField()
    estado = models.CharField(max_length=20)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, db_column="id_usuario")
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE, db_column='id_curso')
    descripcion = models.TextField(blank=True, null=True)

    # ✅ NUEVOS CAMPOS
    peso_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Peso (%) que aporta esta tarea a la nota principal"
    )

    CATEGORIAS = [
        ('P1', 'Permanente 1'),
        ('P2', 'Permanente 2'),
        ('PAR', 'Parcial'),
        ('FIN', 'Final'),
    ]
    categoria = models.CharField(
        max_length=3,
        choices=CATEGORIAS,
        default='P1',
        help_text="Categoría principal a la que pertenece esta tarea"
    )

    class Meta:
        managed = True
        db_table = 'tarea'
    

