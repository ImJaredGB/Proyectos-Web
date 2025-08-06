from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from .models import Usuario
from .forms import UsuarioForm, ResidenteForm
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError

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

def home_view(request):
    return render(request, 'calendario.html')