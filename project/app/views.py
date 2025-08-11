from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from .decorators import login_required_custom
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json



# Vistas html
def registro_residente_view(request):
    error_message = None

    if request.method == 'POST':
        print("📥 Datos recibidos en POST:", request.POST)

        form_usuario = UsuarioForm(request.POST)
        form_residente = ResidenteForm(request.POST)

        print("🧪 Validación de UsuarioForm:", form_usuario.is_valid())
        print("🧪 Validación de ResidenteForm:", form_residente.is_valid())
        print("🛑 Errores UsuarioForm:", form_usuario.errors)
        print("🛑 Errores ResidenteForm:", form_residente.errors)

        if form_usuario.is_valid() and form_residente.is_valid():
            try:
                usuario = form_usuario.save(commit=False)
                usuario.password = make_password(form_usuario.cleaned_data['password'])
                usuario.tipe = 'residente'
                usuario.save()

                residente = form_residente.save(commit=False)
                residente.usuario = usuario
                residente.save()

                print("✅ Usuario y residente guardados correctamente")
                return redirect('login')  # o a donde prefieras

            except IntegrityError as e:
                error_message = "Error de base de datos: " + str(e)
                print("❌ Error en el guardado:", error_message)

        else:
            error_message = "Los datos del formulario no son válidos."

    else:
        form_usuario = UsuarioForm()
        form_residente = ResidenteForm()

    return render(request, 'register.html', {
        'form_usuario': form_usuario,
        'form_residente': form_residente,
        'error_message': error_message,
    })

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(username=email)

            if check_password(password, usuario.password):
                # Aquí puedes guardar el ID del usuario en sesión manualmente si no usas login()
                request.session['usuario_id'] = usuario.id
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Contraseña incorrecta'})

        except Usuario.DoesNotExist:
            return render(request, 'login.html', {'error': 'Usuario no encontrado'})

    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()  # Elimina todos los datos de sesión
    return login_view(request)

from django.shortcuts import render, redirect
from .decorators import login_required_custom

@login_required_custom
def home_view(request):
    if request.method == "POST" and "cerrar_sesion" in request.POST:
        request.session.flush()
        return redirect('login')
    
    return render(request, 'calendario.html')

@login_required_custom
def habitaciones_view(request):
    if request.method == "POST" and "cerrar_sesion" in request.POST:
        request.session.flush()
        return redirect('login')
    
    return render(request, 'habitaciones.html')

@login_required_custom
def usuarios_view(request):
    if request.method == "POST" and "cerrar_sesion" in request.POST:
        request.session.flush()
        return redirect('login')

    usuarios = Usuario.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})

# APIs
@csrf_exempt
def crear_habitacion(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            zona = data.get("zona")
            tamaño = int(data.get("tamaño"))

            # Generar nomenclatura automática
            prefijos = {
                "Castillo": "CP",
                "Restaurante": "RP",
                "Piso": "PP",
                "Vilanova": "VP"
            }
            prefijo = prefijos.get(zona)
            if not prefijo:
                return JsonResponse({"success": False, "error": "Zona inválida"})

            # Buscar cuántas habitaciones hay con ese prefijo
            existentes = Habitacion.objects.filter(zona=zona).count()
            numero = existentes + 1
            nomenclatura = f"{prefijo}{numero}"

            habitacion = Habitacion.objects.create(
                nomenclatura=nomenclatura,
                estado=True,
                tamaño=tamaño,
                zona=zona,
                desactivada=False
            )

            # Crear 4 literas para esta habitación, pero activar solo según el tamaño
            for i in range(1, 5):
                Litera.objects.create(
                    codigo=f"{nomenclatura}_{i}",
                    estado=(i <= tamaño),
                    habitacion=habitacion
                )

            return JsonResponse({
                "success": True,
                "nomenclatura": nomenclatura,
                "tamaño": tamaño,
                "zona": zona
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"error": "Método no permitido"}, status=405)

def obtener_habitaciones_por_zona(request, zona):
    habitaciones = Habitacion.objects.filter(zona=zona).values(
        'nomenclatura', 'estado', 'tamaño', 'desactivada', 'zona'
    )
    return JsonResponse({'habitaciones': list(habitaciones)})


@csrf_exempt
def editar_habitacion(request, nomenclatura):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            habitacion = Habitacion.objects.get(nomenclatura=nomenclatura)
            nuevo_tamaño = int(data.get('tamaño', habitacion.tamaño))
            literas_ocupadas = habitacion.literas.filter(ocupantes__isnull=False).count()
            if nuevo_tamaño < literas_ocupadas:
                return JsonResponse({
                    'error': f"No puedes reducir la habitación a {nuevo_tamaño} literas, ya hay {literas_ocupadas} residentes."
                }, status=400)
            
            # Activar solo las literas dentro del nuevo tamaño, desactivar las demás
            for i in range(1, 5):
                codigo_litera = f"{habitacion.nomenclatura}_{i}"
                litera = habitacion.literas.filter(codigo=codigo_litera).first()
                if litera:
                    litera.estado = (i <= nuevo_tamaño)
                    litera.save()

            habitacion.tamaño = nuevo_tamaño
            habitacion.desactivada = data.get('desactivada', habitacion.desactivada)
            habitacion.save()
            return JsonResponse({'success': True})
        except Habitacion.DoesNotExist:
            return JsonResponse({'error': 'Habitación no encontrada'}, status=404)
        
def listar_literas(request, habitacion):
    try:
        literas = Litera.objects.filter(habitacion__nomenclatura=habitacion)

        data = []
        for litera in literas:
            ocupada = not litera.estado or litera.ocupantes.exists()

            data.append({
                "codigo": litera.codigo,
                "ocupada": ocupada,
                "usuario": f"{litera.ocupantes.first().nombre} {litera.ocupantes.first().apellido}"
                            if litera.ocupantes.exists() else None
            })

        return JsonResponse({"literas": data})
    except Habitacion.DoesNotExist:
        return JsonResponse({"error": "Habitación no encontrada"}, status=404)

    return JsonResponse({"literas": data})

def listar_usuarios(request):
    if request.method == "GET":
        residentes = Residente.objects.select_related('habitacion', 'litera').all()
        data = []

        for r in residentes:
            data.append({
                "id": r.id,
                "nombre": r.nombre,
                "apellido": r.apellido,
                "tipo_documento": r.tipo_documento,
                "documento": r.n_documento,
                "llegada": r.llegada.strftime("%Y-%m-%d") if r.llegada else None,
                "salida": r.salida.strftime("%Y-%m-%d") if r.salida else None,
                "zona": r.habitacion.zona if r.habitacion else "",
                "habitacion": r.habitacion.nomenclatura if r.habitacion else "",
                "litera": r.litera.codigo if r.litera else "",
                "estado": r.estado if hasattr(r, "estado") else True
            })

        return JsonResponse({"usuarios": data})
    
@csrf_exempt
def editar_usuario(request, usuario_id):
    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        residente = Residente.objects.get(id=usuario_id)

        # Actualizar datos básicos
        residente.nombre = data.get('nombre', residente.nombre)
        residente.apellido = data.get('apellido', residente.apellido)
        residente.tipo_documento = data.get('tipo_documento', residente.tipo_documento)
        residente.n_documento = data.get('documento', residente.n_documento)
        residente.llegada = data.get('llegada', residente.llegada)
        residente.salida = data.get('salida', residente.salida)
        residente.estado = "Activo" if data.get('estado', True) else "Inactivo"

        # Asignar habitación si se envía
        habitacion_nom = data.get('habitacion')
        if habitacion_nom:
            try:
                habitacion = Habitacion.objects.get(nomenclatura=habitacion_nom)
                residente.habitacion = habitacion
            except Habitacion.DoesNotExist:
                return JsonResponse({'error': 'Habitación no encontrada'}, status=404)

        # Asignar litera si se envía
        litera_codigo = data.get('litera')
        if litera_codigo:
            try:
                litera = Litera.objects.get(codigo=litera_codigo)
                residente.litera = litera
            except Litera.DoesNotExist:
                return JsonResponse({'error': 'Litera no encontrada'}, status=404)

        residente.save()

        return JsonResponse({'success': True})
    except Residente.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    
def listar_zonas(request):
    zonas = Habitacion.objects.values_list('zona', flat=True).distinct()
    return JsonResponse({"zonas": list(zonas)})

def listar_habitaciones(request):
    zona = request.GET.get('zona')
    if not zona:
        return JsonResponse({"error": "Zona no especificada"}, status=400)

    habitaciones = Habitacion.objects.filter(zona=zona)

    data = []
    for h in habitaciones:
        # Verificar si todas las literas están ocupadas (estado=False)
        todas_ocupadas = not h.literas.filter(estado=True).exists()

        data.append({
            "nomenclatura": h.nomenclatura,
            "zona": h.zona,
            "ocupada": todas_ocupadas  # Usamos estado como referencia
        })

    return JsonResponse({"habitaciones": data})

def obtener_habitaciones_por_zona(request, zona):
    habitaciones = Habitacion.objects.filter(zona=zona)
    data = []

    for hab in habitaciones:
        literas_data = []
        disponibles = 0

        # Filtramos literas activas primero
        literas_activas = hab.literas.filter(estado=True).order_by("codigo")

        for lit in literas_activas:
            ocupante = lit.ocupantes.first()
            esta_ocupada = ocupante is not None

            if not esta_ocupada:
                disponibles += 1

            literas_data.append({
                "codigo": lit.codigo,
                "ocupada": esta_ocupada,
                "usuario": {
                    "nombre": ocupante.nombre,
                    "apellido": ocupante.apellido,
                    "documento": ocupante.n_documento
                } if ocupante else None,
                "llegada": ocupante.llegada.strftime("%Y-%m-%d") if ocupante and ocupante.llegada else None,
                "salida": ocupante.salida.strftime("%Y-%m-%d") if ocupante and ocupante.salida else None
            })

        # Si no hay disponibles, marcamos la habitación como no disponible
        hab.estado = disponibles > 0
        hab.save(update_fields=["estado"])

        data.append({
            "nomenclatura": hab.nomenclatura,
            "estado": 1 if hab.estado else 0,
            "tamaño": hab.tamaño,
            "desactivada": hab.desactivada,
            "disponibles": disponibles,
            "literas": literas_data
        })

    return JsonResponse({"habitaciones": data})