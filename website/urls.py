"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django_browser_reload
from django.contrib import admin
from django.urls import path, include
from webapps.views import auth_login, deconnexion, home, logbook, register, file_upload_view, update_data, getProgram, postProg_info, domaineSelect, sendData, logbook_del_files, connect_profile, ERSloadData, ERSloadTripDetails, sendERSDATA
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [

    

    # path('change_language/', change_language, name='change_language'),
    # Ajoutez vos autres URL ici
    
    # j'importe l'ensemble des urls qui seront déclinées dans mon app palangre syc
    # path("palangre_syc/", include("palangre_syc.urls")),
]

urlpatterns += i18n_patterns(
    path('', home, name="home"),
    path('admin', admin.site.urls),
    path('login', auth_login, name="login"),
    path('register', register, name="register"),
    path('connect-profile/', connect_profile, name='connect_profile'),
    path('logout', deconnexion, name="logout"),
    path('logbook/', logbook, name="logbook"),
    path('logbook/upload', file_upload_view, name="upload_view"),
    path('logbook/update', update_data, name="update"),
    path('<str:domaine>', getProgram, name="getProgram"),
    path('logbook/apply', postProg_info, name="postProg_info"),
    path('logbook/domainselect', domaineSelect, name="domaineSelect"),
    path('logbook/sendData', sendData, name="sendData"),
    path('logbook/del_files', logbook_del_files, name="logbook_del_files"),

    ######################" ERS url #########################
    path('logbook/ERSloadData', ERSloadData, name="ERSloadData"),
    path('logbook/ERSloadTripDetails/<int:trip_id>/', ERSloadTripDetails, name="ERSloadTripDetails"),
    path('logbook/sendERSDATA/<int:trip_id>/', sendERSDATA, name="sendERSDATA"),

    ####################### Fin url #########################
    path("palangre_syc/", include("palangre_syc.urls")),
    path("__reload__/", include("django_browser_reload.urls"))
)

handler404 = 'webapps.views.error_404_view'
