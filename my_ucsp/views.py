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
from .models import Matricula, Curso, Horario, Tarea, Nota, CategoriaPrincipal
from .forms import TareaForm

def index(request): 
    if request.user.is_authenticated:
        matriculas = Matricula.objects.filter(id_usuario=request.user)
        cursos = [m.id_curso for m in matriculas]    
    else:
        cursos = []

    return render(request, "my_ucsp/index.html", {"cursos": cursos})



def calendario(request):
    return render(request, 'my_ucsp/calendario.html')


@login_required
def curso_detalle(request, id_curso):
    curso = get_object_or_404(Curso, id_curso=id_curso)

    # Obtener todas las tareas del curso para este usuario
    tareas = Tarea.objects.filter(id_usuario=request.user, id_curso=curso).order_by('fecha_entrega')

    # Contadores y progreso
    total_tareas = tareas.count()
    entregadas = tareas.filter(estado='ENTREGADO').count()
    progreso = int((entregadas / total_tareas) * 100) if total_tareas > 0 else 0

    # Solo mostrar tareas que no estén entregadas
    tareas_pendientes = tareas.exclude(estado='ENTREGADO')

    return render(request, 'curso-detalle.html', {
        'curso': curso,
        'tareas': tareas_pendientes,
        'total_tareas': total_tareas,
        'entregadas': entregadas,
        'progreso': progreso,
    })


def login_view(request):
    if request.method == "POST":
        email    = request.POST.get('email')
        password = request.POST.get('password')

        # 1. Intentamos encontrar el usuario por email
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect('login')

        # 2. Autenticamos usando su username
        user = authenticate(request,
                            username=user_obj.username,
                            password=password)
        if user is not None:
            # 3. Hacemos login
            login(request, user)

            # 4. Ahora usamos request.user para las matrículas
            tiene_matriculas = Matricula.objects.filter(
                id_usuario=request.user
            ).exists()

            if not tiene_matriculas:
                return redirect('matricular')

            return redirect('index')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect('login')

    # GET: mostrar el formulario
    return render(request, 'my_ucsp/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def matricular_cursos(request):
    user = request.user
    usuario_personal = request.user
    cursos = Curso.objects.all()

    if request.method == 'POST':
        cursos_seleccionados = request.POST.getlist('cursos') 

        for id_curso in cursos_seleccionados:
            curso = get_object_or_404(Curso, id_curso=id_curso)
            Matricula.objects.create(
                id_usuario=usuario_personal,
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


        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('perfil')
    return render(request, 'my_ucsp/editar-perfil.html')

@login_required
def perfil(request):
    user = request.user

    matriculas = Matricula.objects.filter(id_usuario=user)
    if matriculas.exists():
        cursos = [m.id_curso for m in matriculas]
    else:
        cursos = Curso.objects.all()

    return render(request, 'my_ucsp/perfil.html', {
        'perfil': user,
        'cursos': cursos,
    })
    
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password1')
        password2= request.POST.get('password2')

        # 1. Validar campos obligatorios
        if not all([username, email, password, password2]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        # 2. Verificar que las contraseñas coincidan
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register')

        # 3. Comprobar si ya existe un usuario con ese correo
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return redirect('register')

        # 4. Crear el usuario en Django
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            messages.success(request, 'Usuario registrado exitosamente.')
            return redirect('login')
        except IntegrityError:
            messages.error(request, 'Error al registrar usuario.')
            return redirect('register')

    # GET: mostrar el formulario de registro
    return render(request, 'my_ucsp/register.html')



@login_required
def add_tarea(request, id_curso):
    curso = get_object_or_404(Curso, pk=id_curso)

    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.id_curso = curso
            tarea.id_usuario = request.user
            tarea.save()
            messages.success(request, 'Tarea añadida correctamente.')
            return redirect('curso-detalle', id_curso=id_curso)
    else:
        form = TareaForm()

    return render(request, 'add_tarea.html', {
        'form': form,
        'curso': curso
    })

@login_required
def update_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id)
    if request.method == 'POST':
        # Si aún no nos enviaron la nota, mostramos el formulario
        if 'nota_obtenida' not in request.POST:
            return render(request, 'my_ucsp/add_nota.html', {'tarea': tarea})

        # Ya viene la nota, la procesamos:
        nota_val = request.POST['nota_obtenida']
        try:
            nota_val = float(nota_val)
        except ValueError:
            messages.error(request, 'Nota inválida.')
            return redirect('curso-detalle', id_curso=tarea.id_curso.id_curso)

        tarea.estado = 'ENTREGADO'
        tarea.save()

        matricula = Matricula.objects.filter(
            id_usuario=request.user,
            id_curso=tarea.id_curso
        ).first()

        Nota.objects.update_or_create(
            id_tarea=tarea,
            id_matricula=matricula,
            defaults={
                'id_categoria': tarea.id_categoria,
                'nombre_nota': tarea.nombre_tarea,
                'nota_obtenida': nota_val,
                'peso_porcentaje': tarea.peso_porcentaje,
            }
        )

        messages.success(request, 'Tarea entregada y nota registrada.')
        return redirect('curso-detalle', id_curso=tarea.id_curso.id_curso)

    # Si alguien llama GET o un estado inválido, redirigimos
    return redirect('curso-detalle', id_curso=tarea.id_curso.id_curso)


@login_required
def editar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, id_usuario=request.user)

    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            return redirect('curso-detalle', id_curso=tarea.id_curso.id_curso)
    else:
        form = TareaForm(instance=tarea)

    return render(request, 'my_ucsp/editar_tarea.html', {
        'form': form,
        'tarea': tarea
    })


@login_required
def add_nota(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id)

    if request.method == 'POST':
        nota = request.POST['nota']
        tarea.nota = nota
        tarea.save()
        messages.success(request, 'Nota añadida correctamente.')
        return redirect('curso-detalle', id_curso=tarea.id_curso.id_curso)

    return render(request, 'my_ucsp/add_nota.html', {'tarea': tarea})

from django.shortcuts import render, get_object_or_404
from .models import Curso

def simular_nota(request):
    if request.method == 'POST':
        # Aquí procesas request.POST['nota'], guardas en sesión, etc.
        messages.success(request, 'Simulación guardada.')
    return render(request, 'tareas/add_nota.html')


def notas_curso(request, id_curso):
    # 1) Obtén el curso
    curso = get_object_or_404(Curso, id_curso=id_curso)

    # 2) Busca la matrícula de este usuario en ese curso
    matricula = get_object_or_404(
        Matricula,
        id_usuario=request.user,
        id_curso=curso
    )

    # 3) Carga todas las categorías ordenadas
    categorias = CategoriaPrincipal.objects.order_by('id_categoria')

    # 4) Agrupa las notas por categoría
    notas_por_categoria = []
    for cat in categorias:
        notas = Nota.objects.filter(
            id_matricula=matricula,
            id_categoria=cat
        ).select_related('id_tarea')
        notas_por_categoria.append((cat, notas))

    # 5) Renderiza pasando el nuevo contexto
    return render(request, 'notas.html', {
        'curso': curso,
        'notas_por_categoria': notas_por_categoria,
    })



@login_required
def generar_rdf_usuario(request):
    usuario = request.user

    g = Graph()
    EX     = Namespace("http://example.org/ucsp/")
    SCHEMA = Namespace("http://schema.org/")
    g.bind("ex", EX)
    g.bind("foaf", FOAF)
    g.bind("schema", SCHEMA)

    u_uri = URIRef(EX[f"usuario{usuario.id}"])
    g.add((u_uri, RDF.type, FOAF.Person))
    g.add((u_uri, FOAF.name, Literal(usuario.get_full_name(), lang='es')))
    g.add((u_uri, SCHEMA.email, Literal(usuario.email)))

    for m in Matricula.objects.filter(id_usuario=usuario):
        curso = m.id_curso
        c_uri = URIRef(EX[f"curso{curso.id_curso}"])
        g.add((u_uri, EX.matriculadoEn, c_uri))
        g.add((c_uri, RDF.type, SCHEMA.Course))
        g.add((c_uri, SCHEMA.name, Literal(curso.nombre, lang='es')))
        g.add((c_uri, SCHEMA.courseCode, Literal(curso.ciclo)))

        for t in Tarea.objects.filter(id_curso=curso):
            t_uri = URIRef(EX[f"tarea{t.id_tarea}"])
            g.add((c_uri, EX.tieneTarea, t_uri))
            g.add((t_uri, RDF.type, SCHEMA.Task))
            g.add((t_uri, SCHEMA.name, Literal(t.nombre_tarea, lang='es')))
            g.add((t_uri, SCHEMA.dueDate, Literal(t.fecha_entrega, datatype=XSD.date)))

    rdf_data = g.serialize(format='xml')

    return HttpResponse(
        rdf_data,
        content_type='application/rdf+xml',
        headers={'Content-Disposition': 'attachment; filename="mi_perfil_ucsp.rdf"'}
    )
