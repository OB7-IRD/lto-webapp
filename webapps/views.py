from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.timezone import now
from django.contrib import messages
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect

from api_traitement import api_functions
from api_traitement.common_functions import *
from api_traitement.api_functions import *
# from palangre_syc import api

from .form import LTOUserForm

import json
from zipfile import ZipFile
import os

from .models import ConnectionProfile

# Create your views here.
def register(request):
    form = LTOUserForm()
    if request.method == "POST":
        form = LTOUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been successfully created. You can now log in.")
            return redirect("login")

        else:
            messages.error(request, "Erreur lors de l'inscription. Veuillez vérifier les informations fournies.")
    return render(request, "register.html", {"form": form})


def search_in(request, allData, search="Ocean"):
    """Fonction permet d'avoir à partir des données de references les oceans ou les programmes

    Args:
        allData (json): données de references
        search (str): "Ocean" ou "Program"

    Returns:
        prog_dic (json)
    """
    if allData == []: return {}

    if request.session.get('language') == 'fr':
        if search == "Ocean":
            return { val["topiaId"] : val["label2"] for val in allData[search]}
        prog_dic = {}
        if allData == [] :
            return prog_dic

        for val in allData[search]:
            prog_dic[val["topiaId"]] = val["label2"]
        return prog_dic

    elif request.session.get('language') == 'en':
        if search == "Ocean":
            return { val["topiaId"] : val["label1"] for val in allData[search]}
        prog_dic = {}
        if allData == [] :
            return prog_dic

        for val in allData[search]:
            prog_dic[val["topiaId"]] = val["label1"]
        return prog_dic


def auth_login(request):
    message = ""
    if request.method == "POST":
        user_login = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=user_login, password=password)

        if user is not None:
            # Vérifier si le compte a été validé par l'administrateur
            if user.account_valid:
                login(request, user)  # L'utilisateur est connecté
                datat_0c_Pr = {
                    "ocean": None,
                    "program" : None
                }
                request.session['current_user_data'] = {
                    "firstname": request.user.firstname,
                    "lastname" : request.user.lastname,
                    "username" : request.user.username,
                }
                #print(request.session.get('current_user_data'))
                request.session['current_profile_id'] = -1
                request.session['data_Oc_Pr'] = datat_0c_Pr
                return redirect('home')  # Rediriger vers la page d'accueil ou une autre page définie
            else:
                message = _("Votre compte n'a pas encore été validé par l'administrateur.")
        else:
            message = _("Nom d'utilisateur ou mot de passe incorrect")

    return render(request, "login.html", {"message": message})


@login_required
def update_data(request):
    base_url = request.session.get('base_url')
    username = request.session.get('username')
    password = request.session.get('password')
    database = request.session.get('database')
    client_app_version = request.session.get('client_app_version')  # Peut être None
    model_version = request.session.get('model_version')  # Peut être None
    referential_locale = request.session.get('referential_locale')

    # Appel à reload_token avec tous les paramètres requis
    token = api_functions.reload_token(
        username=username,
        password=password,
        base_url=base_url,
        database=database,
        client_app_version=client_app_version,
        model_version=model_version,
        referential_locale=referential_locale
    )

    allData = load_data(token=token, base_url=base_url, forceUpdate=True)
    
    print("="*20, "update_data", "="*20)
    with open('allData.json', 'w', encoding='utf-8') as f:
        json.dump(allData, f, ensure_ascii=False, indent=4)
    
    datat_0c_Pr = {
        "ocean": search_in(request, allData),
        # "domains": {'senne' : allData['seine'], "palangre" : allData['longline']}
        "program": allData['Program']
    }
    request.session['data_Oc_Pr'] = datat_0c_Pr

    return redirect("home")


def deconnexion(request):
    logout(request)
    request.session['token'] = None
    request.session['username'] = None
    request.session['password'] = None
    request.session['database'] = None
    request.session['context'] = None
    request.session['current_profile'] = None
    request.session['current_user_data'] = {
        "firstname": None,
        "lastname" : None,
        "username" : None,
    }

    return redirect("login")


@login_required
def home(request):
    request.session['language'] = request.LANGUAGE_CODE
    # Récupérer les profils de connexion liés à l'utilisateur connecté
    profiles = request.user.connection_profiles.all()

    # Récupérer l'ID du profil actuellement sélectionné depuis la session
    current_profile_id = request.session.get('current_profile_id')

    # Si un profil est sélectionné, récupérer les détails du profil
    current_profile = None
    if current_profile_id:
        try:
            current_profile = ConnectionProfile.objects.get(id=current_profile_id, users=request.user)
        except ConnectionProfile.DoesNotExist:
            current_profile = None

    # print("request_user : ", request.user.email) # Pour Clementine

    # Récupérer les messages de la session (si présent)
    message = request.session.get('message_home')

    return render(request, 'home.html', {
        'profiles': profiles,
        'current_profile': current_profile,
        'message': message
    })

@login_required
def connect_profile(request):
    if request.method == 'POST':
        profile_id = request.POST.get('profile')
        token = ""
        allData = None

        try:
            # Récupérer le profil sélectionné
            profile = ConnectionProfile.objects.get(id=profile_id, users=request.user)

            # Construction dynamique de data_user_connect
            data_user_connect = {
                "config.login": profile.login,
                "config.password": profile.password,
                "config.databaseName": profile.database_alias,
                "referentialLocale": profile.referential_locale or "fr_FR",  # Valeur par défaut
            }

            if profile.client_app_version and profile.model_version:
                data_user_connect["config.clientApplicationVersion"] = profile.client_app_version
                data_user_connect["config.modelVersion"] = profile.model_version

            base_url = profile.url

            try:
                token = api_functions.get_token(base_url, data_user_connect)
                print("Token: ", token)

                current_profile_id = request.session.get('current_profile_id')
                print(" profile_id : ", profile_id)
                print(" current_profile_id : ", current_profile_id)

                if profile_id != current_profile_id:
                    print("="*20, " Changement des données de références ", "="*20)
                    allData = load_data(token=token, base_url=base_url, forceUpdate=True)
                else:
                    print("="*20, " Pas de changement de profil ", "="*20)
                    allData = load_data(token=token, base_url=base_url)

            except Exception as e:
                print("Erreur lors du chargement des données de référence :", e)
                allData = None  # éviter UnboundLocalError

            # Vérification et mise en session
            if (token != "") and (allData is not None and allData != []):
                request.session['token'] = token
                request.session['base_url'] = base_url
                request.session['username'] = profile.login
                request.session['password'] = profile.password
                request.session['database'] = profile.database_alias
                request.session['referential_locale'] = profile.referential_locale or "FR"

                if profile.client_app_version and profile.model_version:
                    request.session['client_app_version'] = profile.client_app_version
                    request.session['model_version'] = profile.model_version
                else:
                    request.session['client_app_version'] = None
                    request.session['model_version'] = None

                request.session['current_profile_id'] = profile_id

                datat_0c_Pr = {
                    "ocean": None,
                    "program": allData["Program"]
                }
                request.session['data_Oc_Pr'] = datat_0c_Pr
                request.session['table_files'] = []
                request.session['message_home'] = ""

                return redirect("home")
            else:
                request.session['message_home'] = _("Impossible de se connecter au serveur. Veuillez vérifier la connexion.")
                return redirect('home')

        except ConnectionProfile.DoesNotExist:
            request.session['base_url'] = None
            request.session['username'] = None
            request.session['password'] = None
            request.session['database'] = None
            request.session['referential_locale'] = None
            request.session['client_app_version'] = None
            request.session['model_version'] = None
            request.session['data_Oc_Pr'] = {
                "ocean": None,
                "program": None
            }
            request.session['message_home'] = _("Pas de profil disponible ou non associé à votre compte.")
            return redirect('home')

    return redirect('home')

@login_required
def logbook(request):
    datat_0c_Pr = request.session.get('data_Oc_Pr')
    apply_conf  = request.session.get('dico_config')

    # Récupérer l'ID du profil actuellement sélectionné depuis la session
    current_profile_id = request.session.get('current_profile_id')

    # Si un profil est sélectionné, récupérer les détails du profil
    current_profile = None
    if current_profile_id:
        try:
            current_profile = ConnectionProfile.objects.get(id=current_profile_id, users=request.user)
        except ConnectionProfile.DoesNotExist:
            current_profile = None

    try:
        file_name = "media/data/" + os.listdir('media/data')[0]
        # Opening JSON file
        f = open(file_name, encoding="utf8")
        # returns JSON object as  a dictionary
        allData = json.load(f)

        datat_0c_Pr.update({"ocean": search_in(request, allData)})
        request.session['data_Oc_Pr'] = datat_0c_Pr
        datat_0c_Pr = request.session.get('data_Oc_Pr')
    except:
        pass

    if datat_0c_Pr['program'] != None:
        print(datat_0c_Pr['program'].keys())
        print("+"*20, "logbook datat_Oc_Pr", "+"*20)

        if request.POST.get('submit'):

            message = tags = ''
            logbooks = os.listdir("media/logbooks")

            #Si validé sans fichier excel televersé
            if logbooks == []:
                print("="*10, "Validé sans fichier excel", "="*10)
                msg = _("Merci de déposer un fichier excel avant de lancer l'extraction de données !")
                messages.error(request, msg)
                tags = "error2"

                return render(request, "logbook.html",{
                    "tags": tags,
                    "alert_message": _("Merci de téléverser un fichier excel"),
                    "ocean_data": datat_0c_Pr["ocean"],
                    "ll_context" : json.dumps(apply_conf),
                    'current_profile': current_profile,
                    "timestamp": now().timestamp()  # pour gérer le cache par rapport au code js

                })
            print(apply_conf)
            # Si le fichier pour les palangre, alors on renvoit vers 'palagre_syc'
            if apply_conf["domaine"] == "palangre":
                logbooks = os.listdir("media/logbooks")
                # print("="*20, "logbook kwargs", "="*20)
                # print(logbooks)
                # print(apply_conf)

                url = reverse('presenting previous trip')
                url = f"{url}?selected_file={logbooks}"
                return redirect(url)

            # sinon on a un fichier senne
            if 0 < len(logbooks) <= 1:
                if apply_conf["ty_doc"] == "ps":
                    info_Navir, data_logbook, data_observateur, message = read_data("media/logbooks/"+ logbooks[0], type_doc="v21")
                if apply_conf["ty_doc"] == "ps2":
                    info_Navir, data_logbook, message = read_data("media/logbooks/"+ logbooks[0], type_doc="v23")

                # Suprimer le ou les fichiers data logbooks
                os.remove("media/logbooks/"+ logbooks[0])

            if message == '' and len(logbooks) > 0:
                 print("len log ", len(logbooks), " messa : ", message)
                 try:
                     file_name = "media/data/" + os.listdir('media/data')[0]
                     # Opening JSON file
                     f = open(file_name, encoding="utf8")
                     # returns JSON object as  a dictionary
                     allData = json.load(f)

                     if apply_conf["ty_doc"] == "ps":
                        allMessages, content_json = build_trip(allData=allData, info_bat=info_Navir, data_log=data_logbook, oce=apply_conf['ocean'], prg=apply_conf['programme'], ob=data_observateur)
                     if apply_conf["ty_doc"] == "ps2":
                        allMessages, content_json = build_trip_v23(allData=allData, info_bat=info_Navir, data_log=data_logbook, oce=apply_conf['ocean'], prg=apply_conf['programme'])

                     try:
                         # Nettoyage de content_json pour rendre tout sérialisable
                         def convert_obj(obj):
                             if isinstance(obj, pd._libs.tslibs.nattype.NaTType):
                                 return None
                             elif isinstance(obj, pd.Timestamp):
                                 return obj.isoformat()
                             return obj

                         def recursive_convert(obj):
                             if isinstance(obj, dict):
                                 return {k: recursive_convert(v) for k, v in obj.items()}
                             elif isinstance(obj, list):
                                 return [recursive_convert(v) for v in obj]
                             else:
                                 return convert_obj(obj)

                         safe_content_json = recursive_convert(content_json)

                         file_name = "media/temporary_files/content_json.json"

                         # créer récursivement tous les dossiers du chemin indiqué, s’ils n’existent pas encore.
                         os.makedirs(os.path.dirname(file_name), exist_ok=True)

                         with open(file_name, 'w', encoding='utf-8') as f:
                             f.write(json.dumps(safe_content_json, ensure_ascii=False, indent=4))

                     except TypeError as e:
                         error_msg = f"Erreur lors de la sauvegarde du fichier JSON : {str(e)}"
                         print(error_msg)
                         messages.error(request, f"Une erreur est survenue pendant l'extraction des données du fichier logbook. <br>"
                                                f"Vérifiez les données ou insérez un notre fichier logbook svp")


                     if allMessages == []:
                         messages.info(request, _("Extration des données avec succès vous pouvez les soumettre maintenant."))
                     elif len(allMessages) == 1 and "Capitaine" in allMessages[0]:
                         messages.info(request, _("Extration des données avec succès.<br>" \
                                                  f"<strong style='color:red;'> Mais : {allMessages[0]} </strong>"))
                     else:
                         for msg in allMessages:
                             messages.error(request, msg)
                         if apply_conf["ty_doc"] == "ps2":
                             tags = "error_v23"
                         else:
                             tags = "error"

                         # Mettre les messages d'erreurs dans un fichier log
                         file_log_name = "media/log/log.txt"

                         with open(file_log_name, 'w', encoding='utf-8') as f_log:
                             log_mess = "\r\r".join(allMessages)
                             f_log.write(log_mess)
                 except UnboundLocalError:
                     messages.error(request, _("Veuillez recharger la page et reprendre votre opération SVP."))
                     tags = "error2"

                     logbooks = os.listdir("media/logbooks")

                     for logbook in logbooks:
                         os.remove("media/logbooks/"+ logbook)

            else:
                messages.error(request, message)
                tags = "error2"

            return render(request, "logbook.html",{
                "tags": tags,
                "ocean_data": datat_0c_Pr["ocean"],
                "ll_context" : json.dumps(apply_conf),
                'current_profile': current_profile,
                "timestamp": now().timestamp()  # pour gérer le cache par rapport au code js
            })

        # else :
        if apply_conf is not None :
            print("="*20, "apply_conf is not None", "="*20)

            print(apply_conf)
            # print(datat_0c_Pr['program'])

            if apply_conf['domaine'] == 'palangre' :
                return render(request, "logbook.html", context={
                    "program_data": datat_0c_Pr['program']['longline'],
                    "ocean_data": datat_0c_Pr["ocean"],
                    "ll_context" : json.dumps(apply_conf),
                    'current_profile': current_profile,
                    "timestamp": now().timestamp()  # pour gérer le cache par rapport au code js
                })
            elif apply_conf['domaine'] == 'senne' :
                return render(request, "logbook.html", context={
                    "program_data": datat_0c_Pr['program']['seine'],
                    "ocean_data": datat_0c_Pr["ocean"],
                    "ll_context" : json.dumps(apply_conf),
                    'current_profile': current_profile,
                    "timestamp": now().timestamp()  # pour gérer le cache par rapport au code js
                })
    # print("="*20, "apply_conf is None", "="*20)
    # print(apply_conf)
    return render(request, "logbook.html", context={
                # "program_data": ll_programs,
                "program_data": datat_0c_Pr["program"],
                "ocean_data": datat_0c_Pr["ocean"],
                "ll_context" : json.dumps(apply_conf),
                'current_profile': current_profile,
                "timestamp": now().timestamp()  # pour gérer le cache par rapport au code js
            })

@login_required
def getProgram(request, domaine):
    """_summary_

    Args:
        request (_type_): _description_
        domaine (_type_): _description_

    Returns:
        _type_: _description_
    """
    datat_0c_Pr = request.session.get('data_Oc_Pr')
    print('views.py getProgram domaine when domaine not selected : ', domaine)

    # if datat_0c_Pr is not None:
    if domaine == "senne" or domaine == "palangre": 
        if domaine == "senne" :
            looking_for = "seine"
        elif domaine == "palangre":
            looking_for = "longline"

        data_0c_Pr = search_in(request, datat_0c_Pr['program'], looking_for)
        print("="*20, "datat_0c_Pr search in", "="*20)
        
        # print(datat_0c_Pr)
        dataPro = {
            "id":[],
            "value":[]
        }
        for key, value in data_0c_Pr.items():
            dataPro["id"].append(key)
            dataPro["value"].append(value)
            
        # print(dataPro)
        return JsonResponse({"dataPro": dataPro})
    else:
        return JsonResponse({})

# @login_required
def postProg_info(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        request.session['dico_config'] = {
            'domaine': request.POST["domaine"],
            'ocean': request.POST["ocean"],
            'programme': request.POST["programme"],
            'ty_doc': request.POST["ty_doc"]
        }
        print(request.session['dico_config'])
        return JsonResponse({"message": "success", 
                            "domaine": request.session.get('dico_config')['domaine']})
    return JsonResponse({"message": _("Veuillez ressayer svp.")})

def logbook_del_files(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if not os.path.exists("media/logbooks"):
            os.makedirs("media/logbooks")

        logbooks_files = os.listdir("media/logbooks")

        if len(logbooks_files) > 0:
            for file in logbooks_files:
                os.remove("media/logbooks/"+ file)

            print("Suppression des logbook trouvés")
        else:
            print("Aucun logbook trouvé dans le cache")
    return JsonResponse({})

@login_required
def domaineSelect(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        logbooks = os.listdir("media/logbooks")

        for logbook in logbooks:
            os.remove("media/logbooks/"+ logbook)

        return JsonResponse({"domaine": request.session.get('dico_config')['domaine']})

@login_required
def sendData(request):
    base_url = request.session.get('base_url')
    username = request.session.get('username')
    password = request.session.get('password')
    database = request.session.get('database')
    client_app_version = request.session.get('client_app_version')  # Peut être None
    model_version = request.session.get('model_version')  # Peut être None
    referential_locale = request.session.get('referential_locale')

    # Appel à reload_token avec tous les paramètres requis
    token = api_functions.reload_token(
        username=username,
        password=password,
        base_url=base_url,
        database=database,
        client_app_version=client_app_version,
        model_version=model_version,
        referential_locale=referential_locale
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        file_name = "media/temporary_files/content_json.json"
        # Opening JSON file
        f = open(file_name, encoding="utf8")
        # returns JSON object as  a dictionary
        content_json = json.load(f)
        route = '/data/ps/common/Trip'
        message, code = api_functions.send_trip(token, content_json, base_url, route)

        if code == 1:
            messages.success(request, message)
            print(1, message)
        elif code == 2:
            messages.error(request, message)
            print(code, message)
        else:
            messages.warning(request, message)
            print(3, message)

        # elif code == 6:
            # messages.add_message(request, code, message) # Tags "error2" cree pour les erreur du serveur
        return JsonResponse({"message": "Success", "code": code, "msg": message})
    return JsonResponse({"message": _("Veuillez ressayer svp.")})

def file_upload_view(request):
    if request.method == "POST":
        file = request.FILES['file']
        fs = FileSystemStorage()
        if (file.name not in os.listdir("media/logbooks")):
            #To copy data to the base folder
            filename = fs.save("logbooks/"+file.name, file)
            uploaded_file_url = fs.url(filename)                 #To get the file`s url

            # print(uploaded_file_url)

        # print("Contenu", request.session['table_files'])
    return render(request, "logbook.html")


##########################################
############    ERS   ####################
##########################################

@login_required
def ERSloadData(request):

    ers_profile = request.user.ers_profile
    # print("ers_profile : ", ers_profile)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and ers_profile:

        _, connectBool = init_connexion_from_profile(ers_profile)

        req1 = "media/requetesSQL/01-trips-list.sql"


        if connectBool:
            dataTripERS = ERSTripList(req1, ers_profile)

            # Conversion DataFrame → liste de dictionnaires pour utiliser au niveau du JS
            dataTripERS_json = dataTripERS.to_dict(orient="records")

            return JsonResponse({
                "message": "Success",
                "connectBool": True,
                "dataTripERS": dataTripERS_json
            })

        return JsonResponse({
            "connectBool": False,
            "message": "Impossible de se connecter à la base ERS (Vérifiez la connexion au VPN)."
        })

    return JsonResponse({
        "connectBool": False,
        "message": "Aucun profil ERS attribué à cet utilisateur."
    })

@login_required
def ERSloadTripDetails(request, trip_id):

    ers_profile = request.user.ers_profile

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and ers_profile:

        _, connectBool = init_connexion_from_profile(ers_profile)

        req2 = 'media/requetesSQL/02-activities-of-a-given-trip-union-q02-q03-q06-q08-q10.sql'
        req5 = "media/requetesSQL/05-landings-of-given-trip.sql"

        if connectBool is True:
            listActivity = ERSloadOneTripDetails(req2, trip_id, ers_profile)
            listLanding = ERSlanding_extraction(req5, trip_id, ers_profile)

            num_activity = len(listActivity)
            num_landing = len(listLanding)
            num_fishing_activity = (listActivity["a_table"] == "fishing_activity").sum()
            num_discards = (listActivity["a_table"] == "discard").sum()

            # print("type :  ", type(num_fishing_activity), num_fishing_activity)

            data = {
                    "num_activity": num_activity,
                    "num_fishing_activity": num_fishing_activity,
                    "num_landing": num_landing,
                    "num_discards": num_discards
                }

            # Convertir toutes les données numpy en types Python natifs
            data = convert_np_types(data)

            return JsonResponse({
                "message": "Success",
                "connectBool": True,
                "data": data
            })

        return JsonResponse({
            "connectBool": False,
            "message": "Impossible de se connecter à la base ERS"
        })

    return JsonResponse({
        "connectBool": False,
        "message": "Aucun profil ERS attribué à cet utilisateur."
    })

@login_required
def sendERSDATA(request, trip_id):

    allData = {}

    try:
        file_name = "media/data/" + os.listdir('media/data')[0]
        # Opening JSON file
        f = open(file_name, encoding="utf8")
        # returns JSON object as  a dictionary
        allData = json.load(f)
    except:
        pass

    ers_profile = request.user.ers_profile

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and ers_profile:

        _, connectBool = init_connexion_from_profile(ers_profile)

        req1 = 'media/requetesSQL/01-trips-list.sql'
        req2 = 'media/requetesSQL/02-activities-of-a-given-trip-union-q02-q03-q06-q08-q10.sql'
        req3 = "media/requetesSQL/03-catches-of-given-fishing-activity.sql"
        req4 = "media/requetesSQL/04-discards-of-given-discard-activity.sql"
        req5 = "media/requetesSQL/05-landings-of-given-trip.sql"

        if connectBool is True:
            df_data = ERSTripList(req1, ers_profile)
            info_bat = ERSVessel_info(df_data, trip_id)
            df_datas_activities = ERSloadOneTripDetails(req2, trip_id, ers_profile)
            df_lands = ERSlanding_extraction(req5, trip_id, ers_profile)

            try:
                ocean = np.unique(df_datas_activities['a_ocean'].dropna())[0].lower()
                find_oce = [(x["topiaId"], x["label2"]) for x in allData['Ocean'] if ocean in x["label2"].lower()]
                oce = find_oce[0][0]
            except:
                oce = request.session.get('dico_config')['ocean']

            prg = request.session.get('dico_config')['programme']

            # Extration des information de la <li> sur laquelle on a cliqué sur "insérer" ou "mettre à jour"
            messages, js_ERScontent = build_trip_ERS(allData, trip_id, info_bat, df_datas_activities, oce, prg, df_lands, req3, req4, ers_profile)

            if js_ERScontent != {} :
                # Envoyer js_ERScontent dans la base de données
                base_url = request.session.get('base_url')
                username = request.session.get('username')
                password = request.session.get('password')
                database = request.session.get('database')
                client_app_version = request.session.get('client_app_version')  # Peut être None
                model_version = request.session.get('model_version')  # Peut être None
                referential_locale = request.session.get('referential_locale')

                # Appel à reload_token avec tous les paramètres requis
                token = api_functions.reload_token(
                    username=username,
                    password=password,
                    base_url=base_url,
                    database=database,
                    client_app_version=client_app_version,
                    model_version=model_version,
                    referential_locale=referential_locale
                )

                route = '/data/ps/common/Trip'
                message_log, code = api_functions.send_trip(token, js_ERScontent, base_url, route)

                if code == 1:
                    # messages.success(request, message_log)
                    print(1, message_log)
                    return JsonResponse({"message": "Success", "code": code, "msg": message_log})
                elif code == 2:
                    # messages.error(request, message_log)
                    print(code, message_log)
                    return JsonResponse({"message": "Success", "code": code, "msg": message_log})
                else:
                    # messages.warning(request, message_log)
                    print(3, message_log)
                    return JsonResponse({"message": "Success", "code": code, "msg": message_log})

                # return JsonResponse({"message": "Success", "code": code, "msg": message_log})

            else:
                return JsonResponse({
                    "message": messages
                })

        return JsonResponse({
            "connectBool": False,
            "message": "Impossible de se connecter à la base ERS"
        })

    return JsonResponse({
        "connectBool": False,
        "message": "Aucun profil ERS attribué à cet utilisateur."
    })


def error_404_view(request, exception):
    return render(request, "404.html")