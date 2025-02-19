from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import LTOUser, ConnectionProfile

# Configuration de l'administration pour LTOUser
class LTOUserAdmin(UserAdmin):
    model = LTOUser
    list_display = ('username', 'email', 'access_level', 'account_valid', 'is_staff')
    list_filter = ('access_level', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email',)
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('firstname', 'lastname', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Access', {'fields': ('access_level', 'account_valid')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'access_level', 'account_valid'),
        }),
    )

# Formulaire personnalisé pour imposer l'unicité du champ "name"
class ConnectionProfileForm(ModelForm):
    class Meta:
        model = ConnectionProfile
        fields = '__all__'

    def clean_name(self):
        name = self.cleaned_data.get('name')
        # Vérifier si un autre profil de l'ensemble excluant le 'id' du profil actuel, avec le même 'name' existe
        if ConnectionProfile.objects.filter(name=name).exclude(id=self.instance.id).exists():
            raise ValidationError("Un profil avec ce nom existe déjà.")
        return name

# Configuration de l'administration pour ConnectionProfile
class ConnectionProfileAdmin(admin.ModelAdmin):
    form = ConnectionProfileForm
    list_display = ('name', 'database_alias', 'url', 'login')
    search_fields = ('name', 'database_alias', 'login')
    filter_horizontal = ('users',)  # Affiche une interface pour ajouter des utilisateurs au profil

# Enregistrement des modèles dans l'administration
admin.site.register(LTOUser, LTOUserAdmin)
admin.site.register(ConnectionProfile, ConnectionProfileAdmin)
