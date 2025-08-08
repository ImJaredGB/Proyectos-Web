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
        
def listar_literas(request):
    zona = request.GET.get("zona")
    if not zona:
        return JsonResponse({"error": "Zona no especificada"}, status=400)

    literas = Litera.objects.filter(habitacion__zona=zona).values_list("codigo", flat=True)

    return JsonResponse({"literas": list(literas)})