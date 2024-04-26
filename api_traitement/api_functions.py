"""
#######################################################
#
# Fonctions relatives à la connexion et requêtes faites à l'api
#
#######################################################
"""

import json
import os
from time import gmtime, strftime, strptime
import requests

from django.contrib.auth import authenticate

from api_traitement.apiFunctions import errorFilter
from api_traitement.common_functions import serialize, pretty_print
from webapps.models import User
from django.utils.translation import gettext as _



########### Token ###########

def get_token(base_url, data):
    """ Fonction qui permet d'avoir un token

    Args:
        base_url (str) : url de base de l'API
        data (json): format de données json exemple ci-dessous
            exemple:
                    data = {
                            "config.login": "username",
                            "config.password": "password",
                            "config.databaseName": "database",
                            "referentialLocale": "FR"
                    }
    Returns:
        token (str)
    """

    url = base_url + "/init/open"
    response = requests.get(url, params=data, timeout=45)
    print(response.url)
    token = response.json()['authenticationToken']

    return token


def is_valid(token):
    """ 
    Fonction booléenne qui test si le token est encore valide
    Args:
        token (str)
    """
    api_base = 'https://observe.ob7.ird.fr/observeweb/api/public/init/information?'
    # Constitution du lien url pour accéder à l'API et fermer la connexion
    api_url = api_base + 'authenticationToken=' + token
    response = requests.get(api_url, timeout=45)
    print("reponse of is valid function ", response.status_code)
    return response.status_code == 200


def reload_token(request, username, password):
    """ Fonction qui recharge un token

    Args:
        request
        username: identifiant de connexion
        password: mot de passe de connexion

    Returns:
        token
    """

    user = authenticate(request, username=username,  password=password)
    data_user = User.objects.get(username=user)

    base_url = data_user.url
    
    print("data_user.database",data_user.database)
    if data_user.database == 'test' :
        data_user.username = 'technicienweb'
                
    data_user_connect = {
        "config.login": data_user.username,
        "config.password": password,
        "config.databaseName": data_user.database,
        "referentialLocale": data_user.ref_language,
    }

    return get_token(base_url, data_user_connect)


def get_all_referential_data(token, module, base_url):
    """Fonction qui récupère les données de références sur le webservice

    Args:
        token
        module: ps ou ll
        base_url: url de connexion - 'https://observe.ob7.ird.fr/observeweb/api/public'

    Returns:
        dict
    """
    url = base_url + "/referential/" + module + "?authenticationToken=" + token
    ac_cap = requests.get(url, timeout=45)
    if ac_cap.status_code == 200:
        dicoModule = {}
        for val in json.loads(ac_cap.text)["content"]:
            vals = val.rsplit('.', 1)[1]
            dicoModule[vals] = []

            for valin in json.loads(ac_cap.text)["content"][val]:
                dicoModule[vals].append(valin)
        print("="*20, "get_all_referential_data", "="*20)
        print(dicoModule)
        return dicoModule
    else:
        return _("Problème de connexion pour recuperer les données")


def load_data(token, base_url, forceUpdate=False):
    """ Fonction qui recupere toutes les données de refences au format JSON de la base de données et stocke ces données
        dans un fichier en local.
        Elle recupere les données de references une fois par jour et elle est utilisé pour faire
        mise à jour des données de references sur le site

    Args:
        token (str): token recuperé
        base_url (str): url de base de l'API
        forceUpdate (bool): True ou False => utilisée dans le cas de la mise à jour des données de references forcées par l'utilisateur

    Returns:
        allData (json)
    """
    print("_"*20, "load_data function starting", "_"*20)
    day = strftime("%Y-%m-%d", gmtime())
    
    # Si les dossiers ne sont pas existant, on les créés
    if not os.path.exists("media/data"):
        os.makedirs("media/data")

    if not os.path.exists("media/temporary_files"):
        os.makedirs("media/temporary_files")

    files = os.listdir("media/data")

    def subFunction(token, day, url):
        ref_common = get_all_referential_data(token, "common", url)
        ps_logbook = get_all_referential_data(token, "ps/logbook", url)
        ps_common = get_all_referential_data(token, "ps/common", url)
        ll_common = get_all_referential_data(token, "ll/common", url)

        program = {
            'Program': {
                'seine' :ps_common["Program"],
                'longline':ll_common["Program"]
            }
        }
        vesselActivity = {
            'VesselActivity': {
                'seine' :ps_common["VesselActivity"],
                'longline':ll_common["VesselActivity"]
            }
        }

        # Suppression des éléments suivant
        del ps_common["Program"]
        del ll_common["Program"]
        del ps_common["VesselActivity"]
        del ll_common["VesselActivity"]

        allData = {**ref_common, **ps_logbook, **ps_common, **ll_common, **program, **vesselActivity}
        # allData = {**ref_common, **ps_logbook, **ps_common}

        ref_common = get_all_referential_data(token, "common", url)
        # ref_common2 ="https://observe.ob7.ird.fr/observeweb/api/public/referential/common?authenticationToken=6811592f-bf3b-4fa0-8320-58a4a58c9ab7"
        ps_logbook = get_all_referential_data(token, "ps/logbook", url)
        ps_common = get_all_referential_data(token, "ps/common", url)
        ll_common = get_all_referential_data(token, "ll/common", url)    
        
        print("="*20, "load_data SubFunction", "="*20)
        # print(ref_common[5:])
        # with open('allData_load.json', 'w', encoding='utf-8') as f:
        #     json.dump(allData, f, ensure_ascii=False, indent=4)
        
        file_name = "media/data/data_" + str(day) + ".json"

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(allData, ensure_ascii=False, indent=4))

        return allData

    if (0 < len(files)) and (len(files) <= 1) and (forceUpdate == False):
        
        last_date = files[0].split("_")[1].split(".")[0]
        last_file = files[0]

        formatted_date1 = strptime(day, "%Y-%m-%d")
        formatted_date2 = strptime(last_date, "%Y-%m-%d")

        # Verifier si le jour actuel est superieur au jour precedent
        if (formatted_date1 > formatted_date2):
            allData = subFunction(token, day, base_url)

            # Suprimer l'ancienne
            os.remove("media/data/" + last_file)
            
            print("="*20, "allData updated", "="*20)
            # print(allData[5:])

        else:
            file_name = "media/data/" + files[0]
            # Opening JSON file
            f = open(file_name , encoding='utf-8')
            # returns JSON object as  a dictionary
            allData = json.load(f)
            
            print("="*20, "allData already existing", "="*20)
            # print(allData)
    else:
        list_file = os.listdir("media/data")
        for file_name in list_file:
            os.remove("media/data/" + str(file_name))

        allData = subFunction(token, day, base_url)
        print("="*20, "subFunction getting allData", "="*20)
        # print(allData[5:])

    return allData

def get_one_from_ws(token, base_url, route, topiaid):
    """ Fonction qui interroge le web service (ws) pour récupérer toutes les données relatives à une route et un topiaid

    Args:
        token (str): token
        base_url: chemin d'accès à la connexion ('https://observe.ob7.ird.fr/observeweb/api/public')
        route: chemin d'accès plus précis (par ex : '/data/ll/common/Trip/')
        topiaid: topiaid avec des '-' à la place des '#'

    Returns:
        file.json: informations relatives au topiaid fourni
    """
    
    headers = {
        'authenticationToken': token, 
    }
    
    params = {
        'config.recursive' : 'true', 
    }
    
    url = base_url + route + topiaid
    
    response = requests.get(url, headers=headers, params = params, timeout=15)

    if response.status_code == 200 :
        # with open(file = "media/temporary_files/previoustrip.json", mode = "w") as outfile:
        #     outfile.write(response.text)
        return response.content
    
    else:
        return None
    
def trip_for_prog_vessel(token, base_url, route, vessel_id, programme_topiaid):
    """
    Pour un navire et un programme donnée, renvoie le topiaid du dernier trip saisi

    Args:
        token
        base_url: 'https://observe.ob7.ird.fr/observeweb/api/public'
        vessel_id: topiaid du navire (avec les '-')
        programme_topiaid: topiaid du programme choisi (avec les '-')

    Returns:
        trip topiaid
    """
    # api_base = 'https://observe.ob7.ird.fr/observeweb/api/'
    api_trip = '?authenticationToken='

    api_vessel_filter = '&filters.vessel_id='
    api_programme_filter = '&filters.logbookProgram_id='
    api_ordeer_filter = '&orders.endDate=DESC'

    api_trip_request = base_url + route + api_trip + token + api_vessel_filter + vessel_id + api_programme_filter + programme_topiaid + api_ordeer_filter
    response = requests.get(api_trip_request, timeout=15)
    return response.content

def send_trip(token, data, base_url, route):
    """ 
    Fonction qui ajoute un trip (marée) dans la base

    Args:
        token (str): token
        data (json): json file (trip) que l'on envoie dans la base
        base_url (str): 'https://observe.ob7.ird.fr/observeweb/api/public' base de connexion à l'api
        route (str):  '/data/ps/common/Trip' ou '/data/ll/common/Trip'
    Returns:
        le json inséré dans le temporary_files 
        text message: logbook bien inséré, ou bien un json d'erreur
    """

    data_json = json.dumps(data, default=serialize)

    headers = {
        "Content-Type": "application/json",
        'authenticationToken': token
    }

    url = base_url + route

    print("Post - send data")
    pretty_print(data)
    
    response = requests.post(url, data=data_json, headers=headers, timeout=45)

    # print(response.status_code, "\n")

    if response.status_code == 200:
        # return json.loads(res.text)
        return (_("Logbook inséré avec success"), 1)
    else:
        with open(file = "media/temporary_files/error.json", mode = "w") as outfile:
            outfile.write(response.text)
        try:
            return (errorFilter(response.text), 2)
            # return json.loads(res.text), 2
        except KeyError:
            # Faire une fonction pour mieux traiter ce type d'erreur
            # print("Message d'erreur: ", json.loads(res.text)["exception"]["result"]["nodes"]) # A faire
            print("Message d'erreur: ", json.loads(response.text)) # A faire
            return (_("L'insertion de cet logbook n'est pas possible. Désolé veuillez essayer un autre"), 3)

def update_trip(token, data, base_url, topiaid):
    """
    Fonction qui met à jour un trip dans la base de données, donc supprime le trip existant pour insérer le nouveau data_json sous le même topiaid

    Args:
        token (str): token
        data (json): json file qu'on envoie dans la base
        base_url (str): 'https://observe.ob7.ird.fr/observeweb/api/public' base de connexion à l'api
        topiaid du trip que l'on veut update (l'ancienne version sera supprimée)
    Returns:
    """

    data_json = json.dumps(data, default=serialize)

    headers = {
        "Content-Type": "application/json",
        'authenticationToken': token,}

    url = base_url + '/data/ll/common/Trip/' + topiaid

    pretty_print(data)
    response = requests.put(url, data=data_json, headers=headers, timeout=15)
    
    print("Code resultat de la requete", response.status_code)
    
    if response.status_code == 200:
        return (_("Logbook inséré avec success"), 1)
    else:
        with open(file = "media/temporary_files/errorupdate.json", mode = "w") as outfile:
            outfile.write(response.text)



def getId_Data(token, base_url, moduleName, argment, route):
    """ Fonction qui permet de retourner un id en fonction du module et de la route envoyé

    Args:
        token (str):token
        base_url (str): url de base de l'API
        moduleName (str): le module de la base de donnée
        argment (str): les arguments de la requete sur le module
        route (str):  chemin de l'API de la requete en fonction de la structure de la base de données.

        exemple:
            moduleName = "Trip"
            route = "/data/ps/common/"
            argment = "startDate=" + ... + "&filters.endDate=" + ... + "&filters.vessel_id=" + ...
            OU
            argment = "startDate=" + ...

    Returns:
        id (str):
    """
    
    headers = {
        "Content-Type": "application/json",
        'authenticationToken': token
    }

    urls = base_url + route + moduleName + "?filters." + argment
    rep = requests.get(urls, headers=headers, timeout=45)

    # print(rep.url)

    if rep.status_code == 200:
        return json.loads(rep.text)["content"][0]["topiaId"]
    else:
        return json.loads(rep.text)["message"]

def check_trip(token, content, base_url):
    """ Fonction qui permet de verifier si la marée a inserer existe déjà dans la base de donnée

    Args:
        token (str): token
        base_url (str): url de base de l'API
        content (json): fragment json de la donnée logbook

    Returns:
        id_ (str): topid de la marée si elle existe
        ms_ (bool): Utilisée pour verifier le statut de la fonction (True == id trouvé)
    """


    start = content["startDate"].replace("T00:00:00.000Z", "")
    end = content["endDate"].replace("T00:00:00.000Z", "")

    vessel_id = content["vessel"].replace("#", "-")

    # print(start, end, vessel_id)

    id_ = ""
    ms_ = True

    try:
        id_ = getId_Data(token, url=base_url, moduleName="Trip", route="/data/ps/common/",
                        argment="startDate=" + start + "&filters.endDate=" + end + "&filters.vessel_id=" + vessel_id)
    except:
        ms_ = False

    return id_, ms_

# Supprimer un trip
def del_trip(token, content):
    """ Fonction qui permet de verifier si la marée a inserer existe déjà dans la base de donnée

    Args:
        token (str): token
        content (json): fragment json de la donnée logbook

    Returns: (json)
    """
    dicts = json.dumps(content)

    headers = {
        "Content-Type": "application/json",
        'authenticationToken': token
    }
    base_url = 'https://observe.ob7.ird.fr/observeweb/api/public'
    id_, ms_ = check_trip(token, content, base_url)

    if ms_ == True:
        
        id_ = id_.replace("#", "-")

        url = 'https://observe.ob7.ird.fr/observeweb/api/public/data/ps/common/Trip/' + id_

        print(id_)

        print("Supprimer")

        res = requests.delete(url, data=dicts, headers=headers, timeout=45)

        print(res.status_code, "\n")

        if res.status_code == 200:
            print("Supprimer avec succes")
            return json.loads(res.text)
        else:
            try:
                return errorFilter(res.text)
            except KeyError:
                print("Message d'erreur: ", json.loads(res.text))
