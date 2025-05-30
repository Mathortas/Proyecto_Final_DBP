from django.shortcuts import render, redirect, get_object_or_404
import datetime
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, FOAF, XSD
from django.contrib.auth.models import User
from .models import Usuario, Matricula, Curso, Horario, Tarea

def index(request): 
    if request.user.is_authenticated:
        perfil = Usuario.objects.filter(correo=request.user.email).first()
        if perfil:
            matriculas = Matricula.objects.filter(id_usuario=perfil)
            cursos = [m.id_curso for m in matriculas]
        else:
            cursos = [] 
    else:
        cursos = []

    return render(request, "my_ucsp/index.html", {"cursos": cursos})



def calendario(request):
    return render(request, 'my_ucsp/calendario.html')


@login_required
def curso_detalle(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)
    horarios = Horario.objects.filter(id_curso=curso)
    tareas   = Tarea.objects.filter(id_curso=curso)
    return render(request, 'my_ucsp/curso-detalle.html', {
        'curso': curso,
        'horarios': horarios,
        'tareas': tareas,
    })



def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect('login')

        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            login(request, user)

            perfil = Usuario.objects.filter(correo=user.email).first()

            if not perfil:
                perfil = Usuario.objects.create(
                    nombre_usuario=user.username,
                    correo=user.email,
                    contrasena=password
                )

            tiene_matriculas = Matricula.objects.filter(id_usuario=perfil).exists()
            if not tiene_matriculas:
                return redirect('matricular')

            return redirect('index')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect('login')

    return render(request, 'my_ucsp/login.html')




def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def matricular_cursos(request):
    user = request.user
    usuario_personal = Usuario.objects.filter(correo=user.email).first()
    cursos = Curso.objects.all()

    if request.method == 'POST':
        cursos_seleccionados = request.POST.getlist('cursos') 

        for id_curso in cursos_seleccionados:
            curso = get_object_or_404(Curso, id_curso=id_curso)
            Matricula.objects.create(
                id_usuario=usuario_personal,
                correo_estudiante=user.email,
                id_curso=curso,
                ciclo=curso.ciclo,
                fecha_matricula=datetime.date.today()
            )

        messages.success(request, 'Cursos matriculados correctamente.')
        return redirect('perfil')

    return render(request, 'my_ucsp/matricula.html', {'cursos': cursos})


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST['nombre']
        user.email = request.POST['email']
        user.save()

        perfil_obj, created = Usuario.objects.update_or_create(       #Actualiza el perfil en la tabla "Usuario" en nuestra base de datos
            correo=user.email,
            defaults={'nombre_usuario': user.username}
        )
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('perfil')
    return render(request, 'my_ucsp/editar-perfil.html')

@login_required
def perfil(request):
    user = request.user
    perfil_obj = Usuario.objects.filter(correo=user.email).first()

    matriculas = Matricula.objects.filter(correo_estudiante=user.email)
    if matriculas.exists():
        cursos = [m.id_curso for m in matriculas]
    else:
        cursos = Curso.objects.all()

    return render(request, 'my_ucsp/perfil.html', {
        'perfil': perfil_obj,
        'cursos': cursos,
    })
    
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not all([username, email, password, password2]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return redirect('register')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            Usuario.objects.create(
                nombre_usuario=username,
                correo=email,
                contrasena=password
            )
            messages.success(request, 'Usuario registrado exitosamente.')
            return redirect('login')

        except IntegrityError:
            messages.error(request, 'Error al registrar usuario.')
            return redirect('register')

    return render(request, 'my_ucsp/register.html')



@login_required
def add_tarea(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)
    if request.method == 'POST':
        nombre    = request.POST['nombre']
        fecha     = request.POST['fecha']
        tipo      = request.POST['tipo']   # NO SE GUARDA EN BD
        estado    = request.POST['estado']
        descripcion = request.POST.get('descripcion', '')

        # Creamos la tarea/prueba (en la tabla Tarea actual)
        Tarea.objects.create(
            nombre_tarea=nombre,
            fecha_entrega=fecha,
            estado=estado,
            id_curso=curso,
            descripcion=descripcion
        )

        messages.success(request, f'{tipo.capitalize()} añadida correctamente.')
        return redirect('curso-detalle', curso_id=curso.id_curso)

    return render(request, 'my_ucsp/add_tarea.html', {'curso': curso})



@login_required
def update_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id)
    if request.method == 'POST':
        nuevo_estado = request.POST['estado']
        if nuevo_estado not in ['pendiente', 'entregada']:
            messages.error(request, 'Estado no válido.')
        else:
            tarea.estado = nuevo_estado
            tarea.save()
            messages.success(request, 'Estado actualizado.')
    return redirect('curso-detalle', curso_id=tarea.id_curso.id_curso)

@login_required
def add_nota(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id)

    if request.method == 'POST':
        nota = request.POST['nota']
        tarea.nota = nota
        tarea.save()
        messages.success(request, 'Nota añadida correctamente.')
        return redirect('curso-detalle', curso_id=tarea.id_curso.id_curso)

    return render(request, 'my_ucsp/add_nota.html', {'tarea': tarea})

@login_required
def generar_rdf_usuario(request):
    usuario = Usuario.objects.get(correo=request.user.email)
    g = Graph()

    EX = Namespace("http://example.org/ucsp/")
    SCHEMA = Namespace("http://schema.org/")
    g.bind("ex", EX)
    g.bind("foaf", FOAF)
    g.bind("schema", SCHEMA)

    user_uri = URIRef(EX[f"usuario{usuario.id_usuario}"])
    g.add((user_uri, RDF.type, FOAF.Person))
    g.add((user_uri, FOAF.name, Literal(usuario.nombre_usuario, lang='es')))
    g.add((user_uri, SCHEMA.email, Literal(usuario.correo)))

    matriculas = Matricula.objects.filter(id_usuario=usuario)
    for matricula in matriculas:
        curso = matricula.id_curso
        curso_uri = URIRef(EX[f"curso{curso.id_curso}"])
        g.add((user_uri, EX.matriculadoEn, curso_uri))
        g.add((curso_uri, RDF.type, SCHEMA.Course))
        g.add((curso_uri, SCHEMA.name, Literal(curso.nombre, lang='es')))
        g.add((curso_uri, SCHEMA.courseCode, Literal(curso.ciclo)))

        tareas = Tarea.objects.filter(id_curso=curso)
        for tarea in tareas:
            tarea_uri = URIRef(EX[f"tarea{tarea.id_tarea}"])
            g.add((curso_uri, EX.tieneTarea, tarea_uri))
            g.add((tarea_uri, RDF.type, SCHEMA.Task))
            g.add((tarea_uri, SCHEMA.name, Literal(tarea.nombre_tarea, lang='es')))
            g.add((tarea_uri, SCHEMA.dueDate, Literal(tarea.fecha_entrega, datatype=XSD.date)))

    rdf_data = g.serialize(format='xml')
    return HttpResponse(
    rdf_data,
    content_type='application/rdf+xml',
    headers={'Content-Disposition': 'attachment; filename="mi_perfil.rdf"'}
)

