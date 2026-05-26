from django.conf import settings
from webapps.models import ConnectionProfile

def global_context(request):
    current_profile = None
    
    if request.user.is_authenticated:
        current_profile_id = request.session.get('current_profile_id')
        if current_profile_id:
            try:
                current_profile = ConnectionProfile.objects.get(
                    id=current_profile_id,
                    users=request.user
                )
            except ConnectionProfile.DoesNotExist:
                current_profile = None

    return {
        'APP_VERSION': settings.APP_VERSION,
        'current_profile': current_profile,
    }