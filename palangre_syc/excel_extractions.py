""" 

Module de fonctions qui permettent l'extraction des données de logbook palangre 
selon le format utilisé par les Seychelles

"""
import pandas as pd
import numpy as np
import re

from django.utils.translation import gettext as _

from api_traitement import common_functions

def extract_vessel_info(df_donnees):
    """
    Extraction des cases 'Vessel Information'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    df_vessel = df_donnees.iloc[7:16, 0]
    # On sépare en deux colonnes selon ce qu'il y a avant et après les ':'
    df_vessel_clean = df_vessel.str.split(':', expand=True)
    # S'assurer que toutes les valeurs sont des chaînes de caractères
    df_vessel_clean = df_vessel_clean.map(lambda x: str(x).strip() if x is not None else '')
    df_vessel_clean.columns = ['Logbook_name', 'Value']
    # On enlève les caractères spéciaux
    df_vessel_clean['Logbook_name'] = common_functions.remove_spec_char_from_list(df_vessel_clean['Logbook_name'])
    df_vessel_clean['Logbook_name'] = df_vessel_clean['Logbook_name'].apply(lambda x: str(x).strip() if x is not None else '')

    return df_vessel_clean


def extract_cruise_info(df_donnees):
    """
    Extraction des cases 'Cruise Information'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    # On extrait les données propres au 'Cruise information'
    df_cruise1 = df_donnees.iloc[9:10, 11:20]
    df_cruise2 = df_donnees.iloc[9:10, 20:29]

    # On supprimes les colonnes qui sont vides
    df_cruise1 = common_functions.del_empty_col(df_cruise1)
    df_cruise2 = common_functions.del_empty_col(df_cruise2)

    np_cruise = np.append(np.array(df_cruise1), np.array(df_cruise2), axis=0)

    # on nettoie la colonne en enlevant les espaces et les ':'
    np_cruise[:, 0] = common_functions.np_removing_semicolon(np_cruise, 0)

    # On applique la fonction strip sur les cellules de la colonnes Valeur,
    # si l'élément correspond à une zone de texte
    vect = np.vectorize(common_functions.strip_if_string)
    np_cruise[:, 1] = vect(np_cruise[:, 1])

    df_cruise = pd.DataFrame(np_cruise, columns=['Logbook_name', 'Value'])
    
    # Nettoyer la colonne 'Logbook_name' en enlevant les espaces et les ':'
    df_cruise['Logbook_name'] = df_cruise.iloc[:, 0].str.replace(':', '').str.strip()

    # Appliquer la fonction strip sur les cellules de la colonne 'Value' si l'élément correspond à une zone de texte
    df_cruise['Value'] = df_cruise.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Appliquer un filtre pour les caractères spéciaux dans la colonne 'Logbook_name' et 'Value'
    df_cruise['Logbook_name'] = common_functions.remove_spec_char_from_list(df_cruise['Logbook_name'])
    df_cruise['Value'] =  common_functions.remove_spec_char_from_list(df_cruise['Value'])
    
    # Supprimer les espaces supplémentaires dans la colonne 'Logbook_name'
    df_cruise['Logbook_name'] = df_cruise['Logbook_name'].str.strip()
    
    return df_cruise

def extract_report_info(df_donnees):
    """
    Extraction des cases 'Report Information'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    # On extrait les données 
    df_report = df_donnees.iloc[7:9, 29:35]

    # On supprime les colonnes qui sont vides
    df_report = df_report.dropna(axis=1, how='all')

    # Nettoyer la colonne 'Logbook_name' en enlevant les espaces et les ':'
    df_report.iloc[:, 0] = df_report.iloc[:, 0].str.replace(':', '').str.strip()

    # Nettoyer la colonne 'Value' en appliquant strip() si l'élément correspond à une chaîne de caractères
    df_report.iloc[:, 1] = df_report.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Renommer les colonnes
    df_report.columns = ['Logbook_name', 'Value']

    # Appliquer un filtre pour les caractères spéciaux dans la colonne 'Logbook_name'
    df_report['Logbook_name'] = common_functions.remove_spec_char_from_list(df_report['Logbook_name'])

    # Supprimer les espaces supplémentaires dans la colonne 'Logbook_name'
    df_report['Logbook_name'] = df_report['Logbook_name'].str.strip()
    
    return df_report

def extract_gear_info(df_donnees):
    """
    Extraction des cases 'Gear'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    # On extrait les données 
    df_gear = df_donnees.iloc[12:16, 11:21]

    # On supprimes les colonnes qui sont vides
    df_gear = common_functions.del_empty_col(df_gear)

    # Nettoyer la colonne 'Logbook_name' en enlevant les espaces et les ':'
    df_gear.iloc[:, 0] = df_gear.iloc[:, 0].str.replace(':', '').str.strip()

    # Nettoyer la colonne 'Value' en appliquant strip() si l'élément correspond à une chaîne de caractères
    df_gear.iloc[:, 1] = df_gear.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Renommer les colonnes
    df_gear.columns = ['Logbook_name', 'Value']

    # Appliquer un filtre pour les caractères spéciaux dans la colonne 'Logbook_name'
    df_gear['Logbook_name'] = common_functions.remove_spec_char_from_list(df_gear['Logbook_name'])

    # Supprimer les espaces supplémentaires dans la colonne 'Logbook_name'
    df_gear['Logbook_name'] = df_gear['Logbook_name'].str.strip()
    
    # On vérifie que les données du excel sont des entiers
    toutes_int = df_gear['Value'].apply(lambda cellule: isinstance(cellule, int)).all()
    if toutes_int:
        # Applique la fonction vect si toutes les cellules sont des entiers
        df_gear['Value'] = np.vectorize(common_functions.strip_if_string)(df_gear['Value'])

    if not df_gear['Value'].apply(lambda x: isinstance(x, int)).all():
        message = _("Les données remplies dans le fichier soumis ne correspondent pas au type de données attendues. Ici on attend seulement des entiers.")
        return df_gear, message

    return df_gear

def extract_line_material(df_donnees):
    """
    Extraction des cases 'Gear'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    # On extrait les données
    df_line = df_donnees.iloc[12:16, 21:29]

    # On supprimes les colonnes qui sont vides
    df_line = common_functions.del_empty_col(df_line)

    # Nettoyer la colonne 'Logbook_name' en enlevant les espaces et les ':'
    df_line.iloc[:, 0] = df_line.iloc[:, 0].str.replace(':', '').str.strip()

    # Nettoyer la colonne 'Value' en appliquant strip() si l'élément correspond à une chaîne de caractères
    df_line.iloc[:, 1] = df_line.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Renommer les colonnes
    df_line.columns = ['Logbook_name', 'Value']

    # Appliquer un filtre pour les caractères spéciaux dans la colonne 'Logbook_name'
    df_line['Logbook_name'] = common_functions.remove_spec_char_from_list(df_line['Logbook_name'])

    # Supprimer les espaces supplémentaires dans la colonne 'Logbook_name'
    df_line['Logbook_name'] = df_line['Logbook_name'].str.strip()
    df_line['Value'] = df_line['Value'].str.strip()
    
    # Filtrer les lignes qui sont cochées
    df_line_used = df_line[(df_line["Value"] != "None") & (df_line["Value"].notna())]
    
    if len(df_line_used) > 1:
        message = _("Ici on n'attend qu'un seul matériau. Veuillez vérifier les données.")
        return df_line_used, message

    if len(df_line_used) == 0:
        message = _("La table entre les lignes 13 à 16 de la colonne 'AC' ne sont pas saisies. Veuillez vérifier les données.")
        return df_line_used, message

    return df_line_used

def extract_target_species(df_donnees):
    """
    Extraction des cases 'Target species'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    # On extrait les données
    df_target = df_donnees.iloc[12:16, 29:34]

    # On supprimes les colonnes qui sont vides
    df_target = common_functions.del_empty_col(df_target)

    # Nettoyer la colonne 'Logbook_name' en enlevant les espaces et les ':'
    df_target.iloc[:, 0] = df_target.iloc[:, 0].str.replace(':', '').str.strip()

    # Nettoyer la colonne 'Value' en appliquant strip() si l'élément correspond à une chaîne de caractères
    df_target.iloc[:, 1] = df_target.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Renommer les colonnes
    df_target.columns = ['Logbook_name', 'Value']

    # Appliquer un filtre pour les caractères spéciaux dans la colonne 'Logbook_name'
    df_target['Logbook_name'] = common_functions.remove_spec_char_from_list(df_target['Logbook_name'])

    # Supprimer les espaces supplémentaires dans la colonne 'Logbook_name'
    df_target['Logbook_name'] = df_target['Logbook_name'].str.strip()
    
    # Filtrer les lignes qui sont cochées
    df_target_used = pd.DataFrame()
    for index, row in df_target.iterrows():
        if row['Value'] is not None:
            df_target_used.loc[len(df_target_used), 'Logbook_name'] = df_target.loc[index, 'Logbook_name']
    
    return df_target_used

def extract_logbook_date(df_donnees):
    """
    Extraction des cases relatives au mois et à l'année du logbook

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    # On extrait les données propres au 'Vessel information'
    df_month = df_donnees.iloc[17, 5]
    df_year = df_donnees.iloc[17, 11]

    month = int(df_month) if isinstance(df_month, (int, float)) and not pd.isna(df_month) else 0
    year = int(df_year) if isinstance(df_year, (int, float)) and not pd.isna(df_year) else 0

    date = {'Logbook_name': ['Month', 'Year'],
            'Value': [int(month), int(year)]}
    df_date = pd.DataFrame(date)
    
    df_date['Logbook_name'] = common_functions.remove_spec_char_from_list(df_date['Logbook_name'])

    return df_date

def extract_bait(df_donnees):
    """
    Extraction des cases relatives au type d'appât utilisé

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    # On extrait les données
    df_squid = df_donnees.iloc[19, 16]
    df_sardine = df_donnees.iloc[19, 20]
    df_mackerel = df_donnees.iloc[19, 24]
    df_muroaji = df_donnees.iloc[19, 28]
    df_other = df_donnees.iloc[19, 32]

    bait = {'Logbook_name': ['Squid', 'Sardine', 'Mackerel', 'Muroaji', 'Other'],
            'Value': [df_squid, df_sardine, df_mackerel, df_muroaji, df_other]}
    
    df_bait = pd.DataFrame(bait)
    
    # Filtrer les lignes qui sont cochées
    df_bait_used = pd.DataFrame()
    for index, row in df_bait.iterrows():
        if row['Value'] is not None:
            df_bait_used.loc[len(df_bait_used), 'Logbook_name'] = df_bait.loc[index, 'Logbook_name']
    
    return df_bait_used

def extract_positions(df_donnees):
    """
    Extraction des cases relatives aux données de position
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    data = df_donnees.iloc[24:55, :7]
    colnames = ['Day', 'Latitude_Degrees', 'Latitude_Minutes', 'Latitude_Direction',
                'Longitude_Degrees', 'Longitude_Minutes', 'Longitude_Direction']
    data.columns = colnames
    
    #  On converti les données de position en degrés décimal
    data['Latitude'] = common_functions.dms_to_decimal(data['Latitude_Degrees'], data['Latitude_Minutes'], data['Latitude_Direction'])
    data['Longitude'] = common_functions.dms_to_decimal(data['Longitude_Degrees'], data['Longitude_Minutes'], data['Longitude_Direction'])
    
    # Supprimer les lignes avec des valeurs nulles et conserver les colonnes d'intérêt
    data = data.dropna(subset=['Latitude', 'Longitude'])
    df_position = data[['Latitude', 'Longitude']]
    
    df_position.reset_index(drop=True, inplace=True)

    return df_position

def get_vessel_activity_topiaid(startTimeStamp, allData):
    """
    Fonction qui prend en argument une heure de depart et qui donne un topiaID de VesselActivity en fonction du type et du contenu de l'entrée
    
    Args:
        startTimeStamp (date): information horaire - si type date alors Fishing operation, sinon on regarde le texte dans la cellule
        allData (json): données de références

    Returns:
        topiaID de l'activité détectée
    """
    if ":" in str(startTimeStamp):
        code = "FO"
        
    elif re.findall(r"[0-9]{4}", startTimeStamp): 
        code = "FO"

    elif re.findall("cruis", startTimeStamp.lower()):
        code = "CRUISE"
    
    elif re.findall("crus", startTimeStamp.lower()):
        code = "CRUISE"

    elif re.findall("port", startTimeStamp.lower()):
        code = "PORT"

    elif startTimeStamp is None:
        return None

    else:
        code = "OTH"

    vessel_activities = allData["VesselActivity"]["longline"]
    for vessel_activity in vessel_activities:
        if vessel_activity.get("code") == code:
            return vessel_activity["topiaId"], vessel_activity["label1"]

    return None

def extract_time(df_donnees, allData):
    """
    Extraction des cases relatives aux horaires des coups de pêche
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df: type horaire, sauf si le bateau est en mouvement
    """
    day = df_donnees.iloc[24:55, 0]
    df_time = df_donnees.iloc[24:55, 7:8]
    colnames = ['Time']
    df_time.columns = colnames
    df_time['Time'] = df_time['Time'].apply(common_functions.convert_to_time_or_text)

    df_time.reset_index(drop=True, inplace=True)

    vessel_activities = np.empty((len(day), 1), dtype=object)
    for ligne in range(len(day)):
        vessel_activity = get_vessel_activity_topiaid(
            df_time.iloc[ligne]['Time'], allData)
        vessel_activities[ligne, 0] = vessel_activity[0]
    np_time = np.column_stack((day, df_time, vessel_activities))
    df_time = pd.DataFrame(np_time, columns=['Day', 'Time', 'VesselActivity'])

    return df_time

def extract_temperature(df_donnees):
    """
    Extraction des cases relatives aux températures
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """

    df_temp = df_donnees.iloc[24:55, 8:9]
    colnames = ['Temperature']
    df_temp.columns = colnames
    df_temp.reset_index(drop=True, inplace=True)
    return df_temp

def extract_fishing_effort(df_donnees):
    """
    Extraction des cases relatives aux efforts de pêche
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    df_fishing_effort = df_donnees.iloc[24:55, [0, 9, 10, 11]].copy()
    df_fishing_effort.columns = ['Day', 'Hooks per basket', 'Total hooks', 'Total lightsticks']
    
    try:
        df_fishing_effort['Total hooks / Hooks per basket'] = common_functions.convert_to_int(df_fishing_effort['Total hooks']) / common_functions.convert_to_int(df_fishing_effort['Hooks per basket'])
    except TypeError:
        df_fishing_effort['Total hooks / Hooks per basket'] = None
        
    df_fishing_effort.reset_index(drop=True, inplace=True)
    return df_fishing_effort

def extract_fish_p1(df_donnees):
    """
    Extraction des cases relatives à ce qui a été pêché
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    df_fishes = df_donnees.iloc[24:55, 12:36]

    colnames = ['No RET SBF', 'Kg RET SBF',
                'No RET ALB', 'Kg RET ALB',
                'No RET BET', 'Kg RET BET',
                'No RET YFT', 'Kg RET YFT', 
                'No RET SWO', 'Kg RET SWO',
                'No RET MLS', 'Kg RET MLS',
                'No RET BUM', 'Kg RET BUM',
                'No RET BLM', 'Kg RET BLM',
                'No RET SFA', 'Kg RET SFA',
                'No RET SSP', 'Kg RET SSP', 
                'No RET OIL', 'Kg RET OIL',
                'No RET MZZ', 'Kg RET MZZ']
    
    df_fishes.columns = colnames
    df_fishes = df_fishes.map(common_functions.zero_if_empty)
    df_fishes.reset_index(drop=True, inplace=True)
    
    return df_fishes
    
def extract_bycatch_p2(df_donnees):
    """
    Extraction des cases relatives à ce qui a été pêché mais accessoires    
    
    Args:
        df_donnees (df): excel p2

    Returns:
        df
    """
    df_bycatch = df_donnees.iloc[15:46, 1:39]

    colnames = ['No RET FAL', 'Kg RET FAL',
                'No ESC FAL', 'No DIS FAL',
                'No RET BSH', 'Kg RET BSH',
                'No ESC BSH', 'No DIS BSH',
                'No RET MAK', 'Kg RET MAK',
                'No ESC MAK', 'No DIS MAK',
                'No RET MSK', 'Kg RET MSK',
                'No ESC MSK', 'No DIS MSK', 
                'No RET SPN', 'Kg RET SPN',
                'No ESC SPN', 'No DIS SPN', 
                'No RET TIG', 'Kg RET TIG',
                'No ESC TIG', 'No DIS TIG', 
                'No RET PSK', 'Kg RET PSK',
                'No ESC PSK', 'No DIS PSK',
                'No ESC THR', 'No DIS THR',
                'No ESC OCS', 'No DIS OCS', 
                'No ESC MAM', 'No DIS MAM', 
                'No ESC SBD', 'No DIS SBD',
                'No ESC TTX', 'No DIS TTX']
    df_bycatch.columns = colnames
    df_bycatch = df_bycatch.map(common_functions.zero_if_empty)
    df_bycatch.reset_index(drop=True, inplace=True)
    return df_bycatch

