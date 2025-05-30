from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, FOAF, XSD

from .models import Usuario, Matricula, Tarea

@login_required
def generar_rdf_usuario(request):
    try:
        usuario = Usuario.objects.get(correo=request.user.email)
    except Usuario.DoesNotExist:
        return HttpResponse("Usuario no encontrado.", status=404)

    g = Graph()
    EX     = Namespace("http://example.org/ucsp/")
    SCHEMA = Namespace("http://schema.org/")
    g.bind("ex", EX)
    g.bind("foaf", FOAF)
    g.bind("schema", SCHEMA)

    u_uri = URIRef(EX[f"usuario{usuario.id_usuario}"])
    g.add((u_uri, RDF.type, FOAF.Person))
    g.add((u_uri, FOAF.name, Literal(usuario.nombre_usuario, lang='es')))
    g.add((u_uri, SCHEMA.email, Literal(usuario.correo)))

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
