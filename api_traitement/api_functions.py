"""
#######################################################
#
# Fonctions relatives à la connexion et requêtes faites à l'api
#
#######################################################
"""

import json
import os
import re
import  numpy as np
import pandas as pd
from time import gmtime, strftime, strptime
import requests
import psycopg2

from django.contrib.auth import authenticate
from django.utils.html import format_html

from api_traitement.common_functions import *

# from webapps.models import User
from webapps.models import LTOUser as User


from django.utils.translation import gettext as _
from configuration.conf import TIMEOUT_VALUE

########### Token ###########

def get_token(base_url, data):
    """ Fonction qui permet d'avoir un token

    Args:
        base_url (str) : url de base de l'API
        data (json): format de données json exemple ci-dessous
            exemple:
                    data = {
                            "config.login": username,
                            "config.password": password,
                            "config.databaseName": database,
                            "config.clientApplicationVersion": client_app_version,
                            "config.modelVersion": model_version,
                            "referentialLocale": "fr_FR"
                    }
    Returns:
        token (str)
        :rtype: object
    """

    url = base_url + "/init/open"
    response = requests.get(url, params=data, timeout=TIMEOUT_VALUE)
    print(response.url)
    token = response.json()['authenticationToken']

    return token


def is_valid(base_url, token):
    """ 
    Fonction booléenne qui test si le token est encore valide
    Args:
        token (str)
    """
    api_base = base_url + '/init/information?'
    # Constitution du lien url pour accéder à l'API et fermer la connexion
    api_url = api_base + 'authenticationToken=' + token
    response = requests.get(api_url, timeout=TIMEOUT_VALUE)
    print("reponse of is valid function ", response.status_code)
    return response.status_code == 200

def reload_token(username, password, base_url, database, client_app_version=None, model_version=None, referential_locale="fr_FR"):
    """ Recharge un token en tenant compte du type de profil

    Args:
        username (str): Login
        password (str): Mot de passe
        base_url (str): URL de base
        database (str): Alias base de données
        client_app_version (str|None): Version de l'app Client obligatoire
        model_version (str): Si None → ancien profil
        referential_locale (str): Langue de référence

    Returns:
        str: Token
    """
    data_user_connect = {
        "config.login": username,
        "config.password": password,
        "config.databaseName": database,
        "referentialLocale": referential_locale
    }

    # Champs supplémentaires uniquement pour les nouveaux profils
    if client_app_version:
        data_user_connect["config.clientApplicationVersion"] = client_app_version
        data_user_connect["config.modelVersion"] = model_version

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
    ac_cap = requests.get(url, timeout=TIMEOUT_VALUE)
    if ac_cap.status_code == 200:
        dicoModule = {}
        for val in json.loads(ac_cap.text)["content"]:
            vals = val.rsplit('.', 1)[1]
            dicoModule[vals] = []

            for valin in json.loads(ac_cap.text)["content"][val]:
                dicoModule[vals].append(valin)
        print("="*20, "get_all_referential_data", "="*20)
        # print(dicoModule)
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
    
    response = requests.get(url, headers=headers, params = params, timeout=TIMEOUT_VALUE)

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
    # print("&"*30, api_trip_request)
    response = requests.get(api_trip_request, timeout=TIMEOUT_VALUE)
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
    
    response = requests.post(url, data=data_json, headers=headers, timeout=TIMEOUT_VALUE)

    # print(response.status_code, "\n")

    if response.status_code == 200:
        # return json.loads(res.text)
        return (_("Logbook inséré avec success"), 1)
    else:
        with open(file = "media/temporary_files/error.json", mode = "w", encoding="utf-8") as outfile:
            outfile.write(response.text)
        try:
            return (error_filter(response.text), 2)
            # return (error_filter(response.text), 6) # 6 pour utiliser le niveau d'erreur personnalisée
            # return json.loads(res.text), 2
        except KeyError:
            try:
                err_data = json.loads(response.text)

                # Cas où on reçoit une erreur inattendue # httpCode 500 du serveur
                if isinstance(err_data, dict) and "exception" in err_data:
                    raw_msg = err_data["exception"]
                    raw_msg_type = err_data["exceptionType"]

                    if 'java.lang.NumberFormatException' == raw_msg_type:
                        # Vérifie si l'erreur mentionne une valeur inattendue
                        if raw_msg['detailMessage']:  # Ex: 'For input string: "2024-12-30T00"'
                            bad_value_match = re.search(r'for input string:\s*"([^"]+)"', raw_msg['detailMessage'].lower())
                            bad_value = bad_value_match.group(1) if bad_value_match else "valeur inconnue"

                            return (_(f"<strong>Erreur de format détectée :</strong> une valeur inattendue <i>\"{bad_value}\" </i> a été trouvée dans le fichier, <br> alors qu'un nombre était attendu. Veuillez corriger cette donnée et réessayer."), 2)

                    # Autres cas d'erreur connus à capter ici si besoin...

                    # Sinon, retourne le message brut avec un avertissement
                    print( f"Erreur inconnue détectée : {raw_msg}.")
                    return (_("Veuillez vérifier les données du fichier ou contacter un administrateur."), 3)

                # Si la structure n'est pas conforme du tout
                return (_("Format d'erreur inattendu. Vérifiez le contenu du fichier."), 3)

            except Exception as e:
                # Si json.loads échoue ou autre erreur
                print("Erreur interne non gérée :", str(e))
                return (_("L'insertion de ce logbook n'est pas possible. Désolé, veuillez essayer un autre."), 3)


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
    response = requests.put(url, data=data_json, headers=headers, timeout=TIMEOUT_VALUE)
    
    print("Code resultat de la requete", response.status_code)
    
    # if response.status_code == 200:
    #     return (_("Logbook inséré avec success"), 1)
    # else:
    #     with open(file = "media/temporary_files/errorupdate.json", mode = "w", encoding="utf-8") as outfile:
    #         outfile.write(response.text)
    #         return (_("L'insertion de cet logbook n'est pas possible. Désolé veuillez essayer un autre"), 3)
        
        
        
    if response.status_code == 200:
        # return json.loads(res.text)
        return (_("Logbook inséré avec success"), 1)
    else:
        with open(file = "media/temporary_files/errorupdate.json", mode = "w", encoding="utf-8") as outfile:
            outfile.write(response.text)
        try:
            return (error_filter(response.text), 2)
            # return (error_filter(response.text), 6) # 6 pour utiliser le niveau d'erreur personnalisée
            # return json.loads(res.text), 2
        except KeyError:
            # Faire une fonction pour mieux traiter ce type d'erreur
            # print("Message d'erreur: ", json.loads(res.text)["exception"]["result"]["nodes"]) # A faire
            # print("Message d'erreur: ", json.loads(response.text)) # A faire
            # return (error_filter(response.text), 2)
            return (_("L'insertion de ce logbook n'est pas possible. Désolé veuillez essayer un autre"), 3)




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
    rep = requests.get(urls, headers=headers, timeout=TIMEOUT_VALUE)

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
        id_ = getId_Data(token, base_url=base_url, moduleName="Trip", route="/data/ps/common/", argment="startDate=" + start + "&filters.endDate=" + end + "&filters.vessel_id=" + vessel_id)
    except:
        ms_ = False

    return id_, ms_

# Supprimer un trip
def del_trip(base_url, token, content):
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
    
    id_, ms_ = check_trip(token, content, base_url)

    if ms_ == True:
        
        id_ = id_.replace("#", "-")

        url = base_url + '/data/ps/common/Trip/' + id_

        print(id_)

        print("Supprimer")

        res = requests.delete(url, data=dicts, headers=headers, timeout=TIMEOUT_VALUE)

        print(res.status_code, "\n")

        if res.status_code == 200:
            print("Supprimer avec succes")
            return json.loads(res.text)
        else:
            try:
                return error_filter(res.text)
            except KeyError:
                print("Message d'erreur: ", json.loads(res.text))


def error_filter(response):
    """
    Permet de simplifier l'affichage des erreurs dans le programme lors de l'insertion des données
    """
    error = json.loads(response)
    text_l = []  # Liste pour stocker les textes d'erreur
    def error_message(nodes, text_list):
        if 'children' in nodes:
            # Appel récursif pour explorer les sous-nœuds
            child_text = str(nodes['datum']['text'])
            if child_text not in text_list:
                text_list.append(child_text)
            return error_message(nodes['children'][0], text_list)

        if 'messages' in nodes:
            temp = nodes['messages']
            text = nodes['datum']['text']

            # Ajout du texte d'erreur dans la liste si pas déjà présent
            if text not in text_list:
                text_list.append(text)

            # text_list = text_list[-1]

            # Expression régulière pour extraire la date et l'heure
            time_pattern = r"(\d{2}/\d{2}/\d{4})"  # pour la date
            date_pattern = r"##(\d{2}:\d{2})##"    # pour l'heure

            # Variables pour stocker la date et l'heure
            date = ""
            heure = ""
            # Recherche du motif dans text_list
            for idx, value in enumerate(text_list):
                match = re.search(time_pattern, value)  # Recherche de la date
                match2 = re.search(date_pattern, value)  # Recherche de l'heure

                if match:
                    date = match.group(1)  # Extraction de la date
                    text_list[idx] = date  # Remplacer la date dans text_list

                elif match2:
                    heure = match2.group(1)  # Extraction de l'heure
                    text_list[idx] = heure  # Remplacer l'heure dans text_list
            try:
                text_list.remove(heure)
                text_list.remove(date)
            except ValueError:
                print("heure ou date non presente dans la liste")

            # Génération du format HTML sous forme de tableau Tailwind
            if date != "" and heure != "":
                return f"""
                <div class="p-4 mb-4 bg-red-100 border-t-4 border-red-500 dark:bg-red-200 rounded-lg" role="alert">
                    <div class="overflow-x-auto">
                        <table class="w-full text-sm text-left text-red-700 border border-red-400 rounded-lg">
                            <thead class="text-xs uppercase bg-red-200 text-red-800">
                                <tr>
                                    <th scope="col" class="px-4 py-2">Date</th>
                                    <th scope="col" class="px-4 py-2">Heure</th>
                                    <th scope="col" class="px-4 py-2">Champs Erreur</th>
                                    <th scope="col" class="px-4 py-2">Message Erreur</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="border-t border-red-400">
                                    <td class="px-4 py-2">{date}</td>
                                    <td class="px-4 py-2">{heure}</td>
                                    <td class="px-4 py-2">{temp[0]['fieldName']}</td>
                                    <td class="px-4 py-2">{temp[0]['message']}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                """
            else:
                return f"""
                <div class="p-4 mb-4 bg-red-100 border-t-4 border-red-500 dark:bg-red-200 rounded-lg" role="alert">
                    <div class="overflow-x-auto">
                        <table class="w-full text-sm text-left text-red-700 border border-red-400 rounded-lg">
                            <thead class="text-xs uppercase bg-red-200 text-red-800">
                                <tr>
                                    <th scope="col" class="px-4 py-2">Champs Erreur</th>
                                    <th scope="col" class="px-4 py-2">Message Erreur</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="border-t border-red-400">
                                    <td class="px-4 py-2">{temp[0]['fieldName']}</td>
                                    <td class="px-4 py-2">{temp[0]['message']}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                """
    all_message = []

    # Vérifie si le premier nœud contient des messages
    if 'messages' in error['exception']['result']['nodes'][0]:
        all_message.append(error_message(error['exception']['result']['nodes'][0], text_l))

    # Parcours des enfants si existants
    try:
        for val in error['exception']['result']['nodes'][0].get('children', []):
            all_message.append(error_message(val, text_l))
    except KeyError:
        pass
    print("Len : ",len(all_message))
    return all_message


###############################################
################ ERS code #####################
###############################################

# Connexion postgreSQL
def init_connexion_from_profile(ers_profile):
    try:
        conn = psycopg2.connect(
            database=ers_profile.database,
            user=ers_profile.user,
            password=ers_profile.password,
            host=ers_profile.host,
            port=ers_profile.port
        )
        return conn, True
    except Exception as e:
        return None, False

def executeScriptsFromFile_prepa(ers_profile, filename, *params):
    """Exécute un script SQL contenu dans un fichier, avec la possibilité de passer plusieurs paramètres.

    Cette fonction lit le contenu d’un fichier SQL, se connecte à la base de données,
    puis exécute la requête en injectant dynamiquement les paramètres fournis.
    Elle affiche le premier résultat renvoyé par la requête.

    Args:
        filename (str): chemin complet du fichier SQL à exécuter.
        *params: un ou plusieurs paramètres à injecter dans la requête SQL (optionnels).

    Returns:
        None
    """
    # Lecture du fichier SQL
    with open(filename, 'r') as fd:
        sqlFile = fd.read()

    # Connexion à la base de données
    conn, _ = init_connexion_from_profile(ers_profile)
    cursor = conn.cursor()

    # Le fichier peut contenir une ou plusieurs requêtes
    sqlCommands = [sqlFile]

    # Exécution de chaque commande SQL
    for command in sqlCommands:
        try:
            # Exécuter la requête avec les paramètres passés
            cursor.execute(command, params)

            # Récupération du premier résultat
            data = cursor.fetchone()
            print(data)
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande : {e}")

    # Fermeture de la connexion
    conn.close()


def executeScriptsFromFile(ers_profile, filename):
    """Exécute un script SQL contenu dans un fichier et renvoie les résultats obtenus.

    Cette fonction lit le contenu d’un fichier SQL, établit une connexion à la base de données,
    puis exécute la ou les requêtes SQL qu’il contient.
    Elle retourne le résultat complet de la ou des requêtes (sous forme de liste de tuples).

    Args:
        filename (str): chemin complet du fichier SQL à exécuter.

    Returns:
        list: liste de tuples contenant les résultats de la requête SQL exécutée.
              Retourne None en cas d’erreur.
    """
    # Lecture du contenu du fichier SQL
    with open(filename, 'r') as fd:
        sqlFile = fd.read()

    # Connexion à la base de données
    conn, _ = init_connexion_from_profile(ers_profile)
    cursor = conn.cursor()

    # Le contenu est traité comme une seule requête (ou un bloc SQL complet)
    sqlCommands = [sqlFile]

    # Exécution de chaque commande SQL
    for command in sqlCommands:
        try:
            cursor.execute(command)
            data = cursor.fetchall()  # Récupération de tous les résultats
            return data
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande : {e}")
            return None
        finally:
            # Fermeture de la connexion
            conn.close()


# New function
def executeScriptsFromFile_id(ers_profile, filename, tp_id):
    """Exécute un script SQL contenant un ou plusieurs paramètres %s.

    Elle renvoie le résultat complet de la requête (liste de tuples).

    Args:
        filename (str): chemin complet du fichier SQL à exécuter.
        tp_id (str | int): identifiant à insérer dans la requête SQL.

    Returns:
        list: liste de tuples contenant les résultats de la requête SQL exécutée.
              Retourne None en cas d’erreur.
    """
    # Lecture du contenu du fichier SQL
    with open(filename, 'r', encoding='utf-8') as fd:
        sqlFile = fd.read()

    # Connexion à la base de données
    conn, _ = init_connexion_from_profile(ers_profile)
    cursor = conn.cursor()

    # Le contenu est traité comme une seule requête (ou un bloc SQL complet)
    sqlCommands = [sqlFile]

    # Exécution de la ou des requêtes SQL
    for command in sqlCommands:
        try:
            # cursor.execute(command, (tp_id,)) # Lorsque j'ai un seul paramettre dans la requête sql avec %s
            cursor.execute(command, tuple([tp_id] * sqlFile.count('%s'))) # marche pour 1 ou plusieurs paramètres (sqlFile.count('%s') => compte le nombre de paramètres dans le fichier SQL)
            data = cursor.fetchall()  # Récupération des résultats
            return data
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande : {e}")
            return None
        finally:
            # Fermeture de la connexion à la base
            conn.close()

def Cardinal_Point():
    path = "media/other_files/Cardinal_Point.csv"
    # Si le fichier n'existe pas, on ne fait rien
    if not os.path.exists(path):
        return False

    # WindDirection
    Cardinal_Point = pd.read_csv(path)
    Abbreviation = [x.lower() for x in list((Cardinal_Point.Abbreviation))]
    Degrees = [float(x.replace("°","")) for x in list((Cardinal_Point["Azimuth Degrees"]))]

    # Convert to Dict
    dictCardinal = {Abbreviation[i]: Degrees[i] for i in range(len(Degrees))}
    return dictCardinal


def convert_np_types(obj):
    if isinstance(obj, np.generic):
        return obj.item()  # Convertit en type natif Python (comme int, float, etc.)
    elif isinstance(obj, dict):
        return {k: convert_np_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np_types(v) for v in obj]
    else:
        return obj

def ERSTripList(req1, ers_profile):
    # Liste des TRIP
    data = executeScriptsFromFile(ers_profile=ers_profile,filename=req1)
    # Transformer le tableau "data" en dataFrame pour faciliter la manipulation des données
    datas = pd.DataFrame(np.array(data))
    # Titrer le tableau
    datas = datas.rename(
            columns={0: "trip_id",
                     1: "trip_start_date",
                     2: "trip_end_date",
                     3: "trip_captain_name",
                     4: "trip_partial_landing",
                     5: "trip_ers_id",
                     6: "trip_departure_harbour_id",
                     7: "trip_departure_harbour_name",
                     8: "trip_departure_harbour_locode",
                     9: "trip_landing_harbour_id",
                     10: "trip_landing_harbour_name",
                     11: "trip_landing_harbour_locode",
                     12: "trip_vessel_turbobat_id",
                     13: "trip_vessel_cfr_id",
                     14: "trip_vessel_name",
                     15: "species_count_at_departure"})

    # Suppression des lignes identiques c.a.d les doublons
    df_data = datas.drop_duplicates(keep='first')

    # Garder les lignes importantes
    df_data = df_data[["trip_id",
                       "trip_start_date",
                       "trip_end_date",
                       "trip_captain_name",
                       "trip_partial_landing",
                       "trip_departure_harbour_name",
                       "trip_departure_harbour_locode",
                       "trip_landing_harbour_name",
                       "trip_vessel_name"]]

    return df_data

def ERSVessel_info(df_data, trip_id):
    # df_data = ERSTripList(ers_profile, req1)

    # Extraction des infos sur le navire pour le trip_id
    data_trip_vessel = df_data[df_data.trip_id == trip_id]

    # supprimer et reinitialiser l'index pas defaut
    data_trip_vessel = data_trip_vessel.reset_index(drop=True)
    # Création du dictionnaire des infos sur le navire
    info_bat = {
            "Navire": str(data_trip_vessel["trip_vessel_name"][0]),
            "Depart_Port": str(data_trip_vessel["trip_departure_harbour_name"][0]),
            "Depart_Date": str(data_trip_vessel["trip_start_date"][0]).split(" ")[0],
            "Arrivee_Port": str(data_trip_vessel["trip_landing_harbour_name"][0]),
            "Arrivee_Date": str(data_trip_vessel["trip_end_date"][0]).split(" ")[0],
            "captain": str(data_trip_vessel["trip_captain_name"][0]),
            "partial_landing": data_trip_vessel["trip_partial_landing"][0],
        }

    return info_bat


def ERSloadOneTripDetails(req2, trip_id, ers_profile):
    # List of activities on this trip_id
    data_activities = executeScriptsFromFile_id(ers_profile=ers_profile, filename=req2, tp_id=trip_id)

    # Transformer le tableau "data" en dataFrame pour faciliter la manipulation des données
    datas_activities = pd.DataFrame(np.array(data_activities))

    # Titrer le tableau
    datas_activities = datas_activities.rename(
            columns={0: "a_table", 1: "catch_id", 2: "trip_id", 3: "trip_vessel_name", 4: "trip_departure_port_name", 5: "trip_departure_port_locode",
                     6: "trip_landing_port_name", 7: "trip_landing_port_locode", 8: "trip_start_date", 9: "trip_start_time", 10: "trip_end_date",
                     11: "trip_end_time", 12: "a_date", 13: "a_time", 14: "fa_end_fishing_date", 15: "fa_end_fishing_time", 16: "a_ocean", 17: "a_latitude",
                     18: "a_longitude", 19: "a_port_name", 20: "a_port_locode", 21: "a_current_direction", 22: "a_current_speed", 23: "a_wind_direction",
                     24: "a_wind_speed", 25: "a_sea_state", 26: "a_sst", 27: "a_school_size", 28: "a_positive_set",
                     29: "a_misc_problems", 30: "a_operation", 31: "a_eez", 32: "gear_type",
                     33: "gear_dimensions", 34: "gear_fishing_depth", 35: "gear_mesh_size", 36: "gear_total_length", 37: "fad_type",
                     38: "fad_has_buoy", 39: "fad_comment", 40: "buoy_type", 41: "buoy_identifier",
                     42: "buoy_comment", 43: "fishing_contexts"})

    # Suppression des lignes identiques c.a.d les doublons
    df_datas_activities = datas_activities.drop_duplicates(keep='first')

    df_datas_activities = df_datas_activities[["a_table",
                                               "catch_id",
                                               "a_date", "a_time",
                                               "a_ocean","a_latitude","a_longitude",
                                               "a_port_name", "a_current_direction", "a_current_speed",
                                               "a_wind_direction", "a_wind_speed", "a_sst",
                                               "a_school_size", "a_positive_set", "a_operation", "a_eez"]]


    return df_datas_activities


def ERSlanding_extraction(req5, trip_id, ers_profile):
    # Extration des données landings
    try:
        data_land = executeScriptsFromFile_id(ers_profile=ers_profile, filename=req5, tp_id=trip_id)
        columns={0: "landing_id",
                1: "trip_id",
                2: "trip_vessel_name",
                3: "trip_start_date",
                4: "trip_start_time",
                5: "trip_end_date",
                6: "trip_end_time",
                7: "specie_fao_id",
                8: "specie_weight_category_id",
                9: "specie_weight_category_ers_id",
                10: "specie_catchweight",
                11: "specie_numberoffished",
                12: "specie_numberoffishedtobelanded"}

        df_land = pd.DataFrame(np.array(data_land))
        df_land = df_land.rename(columns=columns)
        df_land = df_land.drop_duplicates(keep='first') # ou .drop_duplicates()
        df_lands = df_land[["specie_fao_id", "specie_weight_category_id", "specie_weight_category_ers_id", "specie_catchweight", "specie_numberoffished"]]

    except Exception as e: # trip_id n'a pas de données landing
        print("Le trip_id = ", trip_id, " n'a pas de données landing ", "Exception: ", e)
        df_lands = []

    return df_lands


def f_catch(req3, catch_id, ers_profile):

    try:
        data_activities_cts = executeScriptsFromFile_id(ers_profile=ers_profile, filename=req3, tp_id=catch_id)
        datas_activities_catch = pd.DataFrame(np.array(data_activities_cts))
        # Titrer le tableau
        datas_activities_catchs = datas_activities_catch.rename(
                columns={0: "catch_id", 1: "specie_id", 2: "trip_vessel_name", 3: "trip_start_date", 4: "trip_start_time",
                         5: "trip_end_date", 6: "trip_end_time", 7: "fa_id", 8: "fa_date",
                         9: "fa_time", 10: "fa_operation", 11: "fa_eez", 12: "specie_fao_id", 13: "specie_weight_category_id",
                         14: "specie_weight_category_ers_id",
                         15: "specie_catchweight", 16: "specie_numberoffished", 17: "specie_numberoffishedtobelanded"})

        datas_activities_catchs = datas_activities_catchs.drop_duplicates()
        datas_activities_catchs = datas_activities_catchs[["fa_operation","specie_fao_id", "specie_weight_category_ers_id", "specie_weight_category_id","specie_catchweight","specie_numberoffished","specie_numberoffishedtobelanded"]]
        return datas_activities_catchs, True
    except:
        return None, False


def f_discard(req4, discard_id, ers_profile):
    try:
        data_discd = executeScriptsFromFile_id(ers_profile=ers_profile, filename=req4, tp_id=discard_id)
        columns = {0:"discard_id",
                    1:"trip_id",
                    2:"trip_vessel_turbobat_id",
                    3:"trip_vessel_name",
                    4:"trip_start_date",
                    5:"trip_start_time",
                    6:"trip_end_date",
                    7:"trip_end_time",
                    8:"discard_latitude",
                    9:"discard_longitude",
                    10:"species_fao_id",
                    11:"specie_fao_id",
                    12:"specie_weight_category_id",
                    13:"specie_weight_category_ers_id",
                    14:"specie_catchweight",
                    15:"specie_numberoffished",
                    16:"specie_numberoffishedtobelanded"}

        df_discd = pd.DataFrame(np.array(data_discd))
        df_discd = df_discd.rename(columns=columns)
        df_discd = df_discd.drop_duplicates(keep='first') # ou .drop_duplicates()
        df_discds = df_discd[["specie_fao_id", "specie_weight_category_id", "specie_weight_category_ers_id", "specie_catchweight", "specie_numberoffished","specie_numberoffishedtobelanded"]]
        return df_discds, True
    except:
        return None, False


def data_landing(df_landings, allData, not_match_cate=False):
    landing = []
    try:
        for idx, data_s in df_landings.iterrows():

            if  data_s["specie_weight_category_id"] != None and not_match_cate:
                species_id = getId(allData, "Species", argment="faoCode=" + data_s["specie_fao_id"].upper())

                weightCategory_pref = "L-" + data_s["specie_fao_id"] + "-" + str(data_s["specie_weight_category_id"])
                # print(weightCategory_pref)
                try:
                    weightCategory_id = [x['topiaId'] for x in allData["WeightCategory"] if weightCategory_pref in x['code']][0]
                except:
                    weightCategory_id = None

                landing.append(js_landing(species_id, weightCategory_id, weight=data_s["specie_catchweight"]))

            else:
                species_id = getId(allData, "Species", argment="faoCode=" + data_s["specie_fao_id"].upper())
                weightCategory_id = None

                landing.append(js_landing(species_id, weightCategory_id, weight=data_s["specie_catchweight"]))

        return landing
    except:
        return []










