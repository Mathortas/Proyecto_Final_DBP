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
    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='matriculas'
    )
    id_curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        db_column='id_curso',
        related_name='matriculas'
    )
    ciclo = models.CharField(max_length=20)
    fecha_matricula = models.DateField()

    class Meta:
        managed = True
        db_table = 'matricula'

    def __str__(self):
        return f"{self.id_usuario.username} - {self.id_curso.nombre} ({self.ciclo})"


class CategoriaPrincipal(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = True
        db_table = 'categoria_principal'

    def __str__(self):
        return self.nombre

class Tarea(models.Model):
    id_tarea = models.AutoField(primary_key=True)
    nombre_tarea = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_entrega = models.DateField()

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('ENTREGADO', 'Entregado'),
        ('RETRASADO', 'Retrasado'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE'
    )

    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_usuario',
        related_name='tareas'
    )
    id_curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        db_column='id_curso',
        related_name='tareas'
    )
    id_categoria = models.ForeignKey(
        CategoriaPrincipal,
        on_delete=models.RESTRICT,
        db_column='id_categoria',
        related_name='tareas',
        help_text="Categoría principal a la que pertenece esta tarea"
    )
    peso_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Peso (%) que aporta esta tarea a la nota principal"
    )

    class Meta:
        managed = True
        db_table = 'tarea'

    def __str__(self):
        return f"{self.nombre_tarea} [{self.id_categoria.nombre}] ({self.peso_porcentaje}%)"


class Nota(models.Model):
    id_nota = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(
        CategoriaPrincipal,
        on_delete=models.RESTRICT,
        db_column='id_categoria',
        related_name='notas',
        help_text="Nota principal correspondiente"
    )
    id_tarea = models.ForeignKey(
        Tarea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_tarea',
        related_name='notas',
        help_text="Subnota vinculada (tarea, trabajo, etc.)"
    )
    id_matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        db_column='id_matricula',
        related_name='notas'
    )
    nombre_nota = models.CharField(max_length=100, help_text="Título descriptivo de la subnota o examen")
    nota_obtenida = models.DecimalField(max_digits=5, decimal_places=2)
    peso_porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'nota'

    def __str__(self):
        if self.id_tarea:
            return f"{self.id_tarea.nombre_tarea}: {self.nota_obtenida} ({self.peso_porcentaje}%)"
        return f"{self.id_categoria.nombre}: {self.nota_obtenida} ({self.peso_porcentaje}%)"


