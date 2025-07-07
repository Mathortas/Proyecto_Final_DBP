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
from .models import Matricula, Curso, Horario, Tarea, Nota, CategoriaPrincipal, CursoCategoria
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
        form = TareaForm(request.POST, curso=curso)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.id_curso = curso
            tarea.id_usuario = request.user
            tarea.save()
            messages.success(request, 'Tarea o prueba añadida correctamente.')
            return redirect('curso-detalle', id_curso=curso.id_curso)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = TareaForm(curso=curso)

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
    curso = tarea.id_curso  # se usa varias veces, mejor tenerlo aparte

    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea, curso=curso)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Tarea actualizada correctamente.')
                return redirect('curso-detalle', id_curso=curso.id_curso)
            except Exception as e:
                messages.error(request, f'Ocurrió un error al guardar: {e}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = TareaForm(instance=tarea, curso=curso)

    return render(request, 'my_ucsp/editar_tarea.html', {
        'form': form,
        'tarea': tarea,
        'curso': curso  # útil para mostrar {{ curso.nombre }}
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


from django.shortcuts import get_object_or_404, render
from .models import Curso, Matricula, Nota, CategoriaPrincipal, CursoCategoria

def notas_curso(request, id_curso):
    curso = get_object_or_404(Curso, id_curso=id_curso)
    matricula = get_object_or_404(Matricula, id_usuario=request.user, id_curso=curso)

    # ----------- 1. Subcategorías: Permanente 1 y 2 -----------
    permanentes = CategoriaPrincipal.objects.filter(nombre__in=["Permanente 1", "Permanente 2"])
    nota_permanente = []
    suma_ponderada_subnotas = 0
    total_peso_subnotas = 0

    for cat in permanentes:
        notas = Nota.objects.filter(
            id_matricula=matricula,
            id_categoria=cat,
            id_tarea__isnull=False
        ).select_related('id_tarea')

        rel = CursoCategoria.objects.filter(id_curso=curso, id_categoria=cat).first()
        peso_sub = rel.peso if rel else cat.peso_porcentaje
        cat.peso = peso_sub

        suma = sum(n.nota_obtenida * (n.peso_porcentaje / 100) for n in notas if n.nota_obtenida is not None)
        suma_ponderada_subnotas += suma
        total_peso_subnotas += peso_sub

        nota_permanente.append((cat, notas))

    # ------------ 2. Peso y contribución de Nota Permanente ------------

    # Obtener categoría principal "Nota Permanente"
    cat_nota_perma = CategoriaPrincipal.objects.get(nombre="Nota Permanente")
    rel_perma = CursoCategoria.objects.filter(id_curso=curso, id_categoria=cat_nota_perma).first()
    peso_permanente = rel_perma.peso if rel_perma else cat_nota_perma.peso_porcentaje

    promedio_permanente = suma_ponderada_subnotas if total_peso_subnotas > 0 else None
    contribucion_permanente = (promedio_permanente * peso_permanente / 100) if promedio_permanente is not None else 0

    # ------------ 3. Otras categorías principales ------------

    principales = CategoriaPrincipal.objects.filter(tipo='PRINCIPAL').exclude(
        nombre__in=["Permanente 1", "Permanente 2", "Nota Permanente"]
    )
    otras_categorias = []
    promedio_final = contribucion_permanente

    for cat in principales:
        notas = Nota.objects.filter(
            id_matricula=matricula,
            id_categoria=cat,
            id_tarea__isnull=True  # solo evaluaciones, no tareas
        )

        rel = CursoCategoria.objects.filter(id_curso=curso, id_categoria=cat).first()
        peso_cat = rel.peso if rel else cat.peso_porcentaje
        cat.peso = peso_cat

        total = sum(n.nota_obtenida for n in notas if n.nota_obtenida is not None)
        cantidad = len(notas)
        promedio_cat = (total / cantidad) if cantidad else None
        contribucion = (promedio_cat * peso_cat / 100) if promedio_cat is not None else 0

        if promedio_cat is not None:
            promedio_final += contribucion

        otras_categorias.append((cat, notas, promedio_cat, contribucion))

    # ------------ 4. Render ------------

    return render(request, 'notas.html', {
        'curso': curso,
        'nota_permanente': nota_permanente,
        'peso_permanente': peso_permanente,
        'promedio_permanente': promedio_permanente,
        'contribucion_permanente': contribucion_permanente,
        'otras_categorias': otras_categorias,
        'promedio_final': promedio_final,
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
