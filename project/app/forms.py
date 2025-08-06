from django import forms
from .models import Usuario, Residente

class UsuarioForm(forms.ModelForm):
    confirmar_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Usuario
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
        labels = {
            'username': 'Correo electrónico'
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirmar_password")
        if p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

class ResidenteForm(forms.ModelForm):
    class Meta:
        model = Residente
        fields = [
            'nombre',
            'apellido',
            'n_documento',
            'nacionalidad',
            'telefono',
        ]