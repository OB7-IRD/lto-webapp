# -*- coding: utf-8 -*-
""" 

Module de fonctions communes et générales à l'application indépendamment de la pêcherie. 

"""
import json
import datetime
import re
import openpyxl
import pandas as pd
import numpy as np

def load_json_file(file_path):
    """ Fonction qui charge un fichier json enregistré dans un dossier donné en argument et le renvoie

    Args:
        file_path
        
    Returns:
        dict: fichier json en format dictionnaire
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file '{file_path}': {e}")
        return None
    
def serialize(obj): 
    """ 
    Serialize obj dans un format json de type date, int ou str.
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, np.int64) or isinstance(obj, np.int32):
        return int(obj)
    return str(obj)
    # raise TypeError("Type not serializable")

def pretty_print(json_data, file="media/temporary_files/created_json_file.json", mode="a"):
    """ Fonction qui affiche le fichier json avec les bonnes indentations un fichier json

    Args:
        json_data (json): Données json en entrée
        file (str, optional): Nom de fichier json de sortie "created_json_file.json".
        mode (str, optional): Defaults to "a" pour "append" - "w" pour "write"
    """

    json_formatted_str = json.dumps(
        json_data, indent=2, default=serialize)
    with open(file, mode) as outfile:
        outfile.write(json_formatted_str)


def del_empty_col(dataframe):
    """ Fonction qui supprime la colonne si elle ne contient pas d'information

    Args:
        dataframe: avec des potentielles colonnes vides (cellules mergées)

    Returns:
        dataframe: uniquement avec des éléments
    """
    colonnes_a_supprimer = [
        colonne for colonne in dataframe.columns if all(dataframe[colonne].isna())]
    dataframe.drop(columns=colonnes_a_supprimer, inplace=True)
    return dataframe

def strip_if_string(element):
    """
    Fonction qui applique la fonction python strip() si l'élement est bien de type texte
    """
    return element.strip() if isinstance(element, str) else element

def remove_spec_char_from_list(char_list):
    """
    Fonction qui applique remove_spec_char à chaque élément d'une liste de chaînes
    """
    return [re.sub("[^A-Z a-z0-9]", "", str(item), 0, re.IGNORECASE) for item in char_list]

def convert_to_int(value):
    """
    Vérifie si la valeur est numérique ou peut être transformée en numérique (integer).

    Args:
    value: L'élément à vérifier.

    Returns:
    bool: la valeur si elle est de type numérique et un message sinon.
    """
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
        try:
            int(value)
            return int(value)
        except ValueError:
            return value
    return value

def convert_to_time_or_text(value):
    """
    Fonction qui converti la cellule en time si elle est au format type time ou date dans le excel
    et qui laisse au format texte (cruising, in port etc) si la cellule est au format texte
    """
    if isinstance(value, str):
        if re.findall(r"[0-9]{4}", value):
            time_value = value[:2]+ ":"+ value[2:]+":00"
            return datetime.datetime.strptime(time_value, '%H:%M:%S').time().strftime('%H:%M:%S')
        if re.match("[0-9]{2}:[0-9]{2}:[0-9]{2}", value):
            return datetime.datetime.strptime(value, '%H:%M:%S').time().strftime('%H:%M:%S')
    
        elif re.match("[0-9]{2}:[0-9]{2}", value.strip()):
            return value.strip() + ':00'
        elif re.match("[0-9]{1}:[0-9]{2}", value.strip()):
            return '0' + value.strip() + ':00'
        
        return value
    elif isinstance(value, datetime.datetime):
        date_time = value.time()
        if hasattr(date_time, 'strftime'):
            return date_time.strftime('%H:%M:%S')
        return str(date_time)
    return str(value)


def np_removing_semicolon(numpy_table, num_col):
    """
    Fonction qui prend une numpy table et ne retourne que la partie avant les deux point (:) de la colonne demandée
    """
    return np.array([s.partition(':')[num_col].strip() for s in numpy_table[:, num_col]])

def dms_to_decimal(degrees, minutes, direction):
    """Transforme des degrés minutes secondes en décimal

    Args:
        degrees (int), minutes (int): value
        direction (str): N S E W

    Returns:
        float: value
    """
    if degrees is None:
        return None
    
    degrees = degrees.fillna(0)
    minutes = minutes.fillna(0)
    
    degrees = degrees.astype(int)
    minutes = minutes.astype(int)

    decimal_degrees = degrees + minutes / 60.0
    decimal_degrees = np.where(direction.isin(['S', 'W']), -decimal_degrees, decimal_degrees)
    return decimal_degrees

def zero_if_empty(value):
    """
    Remplace par 0 quand la case est vide
    """
    if value == "None" or pd.isna(value):
        return 0
    elif isinstance(value, str) and (value == "" or re.search(r"\S*", value)):
        return 0
    else:
        return int(value)

def remove_if_nul(df, column):
    """ Function that remove the last rows if the value is null in a specific column
    Args:
        df (dataframe)
        column: column you want to check
    """
    while df[column].iloc[-1] == 0:
        df = df[:-1]
    return df

def read_excel(logbook_file_path, num_page):
    """ 
    Fonction qui extrait les informations d'un fichier excel en dataframe

    Args:
        logbook_file_path: lien vers le fichier contenant le logbook
        num_page (int): numéro de page à extraire (1, 2 etc ...)

    Returns:
        (dataframe): du fichier excel
    """
    classeur = openpyxl.load_workbook(filename=logbook_file_path, data_only=True)
    noms_feuilles = classeur.sheetnames
    feuille = classeur[noms_feuilles[num_page - 1]]
    df_donnees = pd.DataFrame(feuille.values)
    classeur.close()
    return df_donnees


def get_list_harbours(allData):
    """
    Args:
        allData

    Returns:
        list: all the enabled ports (topiaId and label2)
    """

    harbours = allData["Harbour"]
    sorted_list_harbours = [{'topiaId': harbour.get('topiaId'), 'label2': harbour.get('label2')} 
                        for harbour in harbours if harbour.get('status') == 'enabled']
    sorted_list_harbours.sort(key=lambda x: x['label2'])

    return sorted_list_harbours


def from_topiaid_to_value(topiaid, lookingfor, label_output, allData, domaine=None):
    """
    Fonction générale qui retourne le label output pour un topiad donné 
    dans la base common ou longliner

    Args:
        topiad
        lookingfor: catégorie issu du WS dans laquelle on veut chercher notre topiaid
        label_output: ce qu'on veut présenter (label, nom, espèce ...)
        domaine si nécessaire (palangre, senne)

    Returns:
        nom souhaité associé au topotiad
    """
    
    if lookingfor == 'VesselActivity' or lookingfor == 'Program':
        if domaine is None :
            print("Error il faut préciser un domaine")
            return None
        else :
            if domaine == 'palangre':
                domaine_en = str('longline')
            else:
                domaine_en = str('seine')
            
            for element in allData[lookingfor][domaine_en]: 
                if element['topiaId'] == topiaid:
                    return element[label_output]
        
    else:
        if allData[lookingfor] is not None:
            for element in allData[lookingfor]:
                if element['topiaId'] == topiaid:
                    return element[label_output]
        else:
            print("please do check the orthographe of looking for element")
            return None

def getId(allData, moduleName, argment, nbArg=False, domaine=None):
    """Fonction qui retourne l'ID d'un module en fonction des arguments donnés

    Args:
        allData (json): données de references
        moduleName (str): le module de la base de donnée
        argment (str): les arguments de la requete sur le module
        domaine (str): "seine" ou "longline" dans le cas ou nous voulons recuperer les id de VesselActivity
        nbArg (bool): permet de signifier le nombre d'argument dont on aura besoin pour trouver l'ID
               par defaut quand c'est False nous avons 1 argument en paramentre
               si c'est True, nous avons 2 arguments en parametre

    Returns:
         topiad (str)
    """
    message = ""
    Id = ""
    dataKey = [k for (k, v) in allData.items()]

    if moduleName in dataKey:
        if domaine != None:
            tempDic = allData[moduleName][domaine]
        else:
            tempDic = allData[moduleName]

        if nbArg:
            # 2 arguments
            argTab = argment.split("&filters.")
            argments = [argTab[0].split("="), argTab[1].split("=")]
            for val in tempDic:
                if (val[argments[0][0]] == argments[0][1]) and (val[argments[1][0]] == argments[1][1]):
                    Id = val['topiaId']
        else:
            # 1 argument
            argments = argment.split("=")
            for val in tempDic:
                if val[argments[0]] == argments[1]:
                    Id = val['topiaId']

        if Id == "":
            # message = "Aucun topiad"
            Id = None
    else:
        # message = "Le module: "+ module + " n'existe pas"
        Id = None

    return Id

def search_in(allData, search="Ocean"):
    """Fonction permet d'avoir à partir des données de references les oceans ou les programmes

    Args:
        allData (json): données de references
        search (str): "Ocean" ou "Program"

    Returns:
        prog_dic (json)
    """
    if allData == []: return {}

    if search == "Ocean":
        return { val["topiaId"] : val["label2"] for val in allData[search]}
    prog_dic = {}
    if allData == [] :
        return prog_dic

    for val in allData[search]:
        prog_dic[val["topiaId"]] = val["label2"]
    return prog_dic

def getSome(allData, moduleName, argment):
    """Permet de retouner un dictionnaire de donnée du module dans une liste (tableau)

    Args:
        allData (json): données de references
        moduleName (str): le module de la base de donnée
        argment (str): les arguments de la requete sur le module

    Returns:
        (list)
    """
    tempDic = {}
    dico = {}
    dataKey = [k for (k, v) in allData.items()]

    if moduleName in dataKey:
        tempDic = allData[moduleName]
        argments = argment.split("=")
        for val in tempDic:
            if val[argments[0]].lower() == argments[1].lower():
                dico = val

    return [dico]

def getAll(allData, moduleName, type_data="dictionnaire"):
    """Permet de retourner un dictionnaire ou un tableau

    Args:
        allData (json): données de references
        moduleName (str): le module de la base de donnée
        type_data (str): "dictionnaire" ou "tableau"

    Returns:
        tab (list)
        dico (dict)
    """
    if type_data == "tableau":
        tab = []
        for val in allData[moduleName]:
            tab.append((val["topiaId"], val["label1"]))

        return tab
    else:
        dico = {}
        for val in allData[moduleName]:
            dico[val["code"]] = val["topiaId"]

        return dico




