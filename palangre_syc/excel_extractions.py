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


def extract_cruise_info(df_donnees, version):
    """
    Extraction des cases 'Cruise Information'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    # On extrait les données propres au 'Cruise information'
    if version == "ll_17.6":
        df_cruise1 = df_donnees.iloc[[9], [11, 16]]
        df_cruise2 = df_donnees.iloc[[9], [20, 25]]
    elif version == "ll_26":
        df_cruise1 = df_donnees.iloc[[9], [9, 14]]
        df_cruise2 = df_donnees.iloc[[9], [18, 23]]

    # Forcer les mêmes noms de colonnes
    df_cruise1.columns = ['Logbook_name', 'Value']
    df_cruise2.columns = ['Logbook_name', 'Value']

    # Concaténation verticale
    df_cruise = pd.concat([df_cruise1, df_cruise2], axis=0, ignore_index=True)

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

def extract_report_info(df_donnees, version):
    """
    Extraction des cases 'Report Information'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    if version == "ll_17.6":
        df_report = df_donnees.iloc[7:9, 29:35]
    elif version == "ll_26":
        df_report = df_donnees.iloc[7:9, 27:33]

    # On supprime les colonnes qui sont vides
    df_report = df_report.dropna(axis=1, how='all')
    
    # Nettoyer la colonne 'Logbook_name' en enlevant les espaces et les ':'
    df_report.iloc[:, 0] = df_report.iloc[:, 0].str.replace(':', '').str.strip()

    if df_report.shape[1] < 2:
        # Renommer les colonnes
        df_report.columns = ['Logbook_name']
        # Appliquer un filtre pour les caractères spéciaux dans la colonne 'Logbook_name'
        df_report['Logbook_name'] = common_functions.remove_spec_char_from_list(df_report['Logbook_name'])
        # Supprimer les espaces supplémentaires dans la colonne 'Logbook_name'
        df_report['Logbook_name'] = df_report['Logbook_name'].str.strip()
        df_report['Value'] = pd.NA
    else:
        # Nettoyer la colonne 'Value' en appliquant strip() si l'élément correspond à une chaîne de caractères
        df_report.iloc[:, 1] = df_report.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Renommer les colonnes
        df_report.columns = ['Logbook_name', 'Value']

        # Appliquer un filtre pour les caractères spéciaux dans la colonne 'Logbook_name'
        df_report['Logbook_name'] = common_functions.remove_spec_char_from_list(df_report['Logbook_name'])

        # Supprimer les espaces supplémentaires dans la colonne 'Logbook_name'
        df_report['Logbook_name'] = df_report['Logbook_name'].str.strip()

    return df_report

def extract_gear_info(df_donnees, version):
    """
    Extraction des cases 'Gear'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    if version == "ll_17.6":
        df_gear = df_donnees.iloc[12:16, 11:21]
    elif version == "ll_26":
        df_gear = df_donnees.iloc[12:16, 9:19]
    
    # On supprimes les colonnes qui sont vides
    df_gear = common_functions.del_empty_col(df_gear)

    # Nettoyer la colonne 'Logbook_name' en enlevant les espaces et les ':'
    df_gear.iloc[:, 0] = df_gear.iloc[:, 0].str.replace(':', '').str.strip()

    # Nettoyer la colonne 'Value' en appliquant strip() si l'élément correspond à une chaîne de caractères
    if df_gear.shape[1] != 1:
        df_gear.iloc[:, 1] = df_gear.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) else x)
    else:
        df_gear['Value'] = None
        
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

def extract_line_material_v17(df_donnees):
    """
    Extraction des cases 'Gear' selon la version du logbook v.17.6 de 2024

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
        return df_line_used

    if len(df_line_used) == 0:
        message = _("La table entre les lignes 13 à 16 de la colonne 'AC' ne sont pas saisies. Veuillez vérifier les données.")
        return df_line_used, message

    return df_line_used

def extract_line_material_v26(df_donnees):
    """
    Extraction des cases 'Gear' selon la version du logbook v.18 de 2026

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """

    df_line = df_donnees.iloc[12:16, 19:27]
    df_line = common_functions.del_empty_col(df_line)

    # Nettoyer la colonne 'Logbook_name' en enlevant les espaces et les ':'
    df_line.iloc[:, 0] = df_line.iloc[:, 0].str.replace(':', '').str.strip()

    # Nettoyer la colonne 'Value' en appliquant strip() si l'élément correspond à une chaîne de caractères
    df_line.iloc[:, 1] = df_line.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) else x)
    # Renommer les colonnes
    df_line.columns = ['Logbook_name', 'Value']

    # Appliquer un filtre pour les caractères spéciaux dans la colonne 'Logbook_name'
    df_line['Logbook_name'] = common_functions.remove_spec_char_from_list(df_line['Logbook_name'])
    df_line['Value'] = common_functions.remove_spec_char_from_list(df_line['Value'])
    
    # Supprimer les espaces supplémentaires dans la colonne 'Logbook_name'
    df_line['Logbook_name'] = df_line['Logbook_name'].str.strip()
    df_line['Value'] = df_line['Value'].str.strip()

    return df_line

def extract_target_species(df_donnees, version):
    """
    Extraction des cases 'Target species'

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    if version == "ll_17.6":
        df_target = df_donnees.iloc[12:16, 29:34]
    elif version == "ll_26":
        df_target = df_donnees.iloc[12:16, 27:32]
    
    # On supprimes les colonnes qui sont vides
    df_target = common_functions.del_empty_col(df_target)

    # Nettoyer la colonne 'Logbook_name' en enlevant les espaces et les ':'
    df_target.iloc[:, 0] = df_target.iloc[:, 0].str.replace(':', '').str.strip()
    
    # Nettoyer la colonne 'Value' en appliquant strip() si l'élément correspond à une chaîne de caractères
    # df_target.iloc[:, 1] = df_target.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) and pd.notna(x) else x)
    if df_target.shape[1] > 1:
        df_target.iloc[:, 1] = df_target.iloc[:, 1].apply(lambda x: x.strip() if isinstance(x, str) else x)
    else:
        # Pas de colonne "Value" → aucun target bait coché
        return pd.DataFrame(columns=["Logbook_name"])

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

def extract_logbook_date(df_donnees, version):
    """
    Extraction des cases relatives au mois et à l'année du logbook

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    # On extrait les données propres au 'Vessel information'
    df_month = df_donnees.iloc[17, 5]
    if version == "ll_17.6":
        df_year = df_donnees.iloc[17, 11]
    elif version == "ll_26":
        df_year = df_donnees.iloc[17, 8]

    month = int(df_month) if isinstance(df_month, (int, float)) and not pd.isna(df_month) else 0
    year = int(df_year) if isinstance(df_year, (int, float)) and not pd.isna(df_year) else 0

    date = {'Logbook_name': ['Month', 'Year'],
            'Value': [int(month), int(year)]}
    df_date = pd.DataFrame(date)
    
    df_date['Logbook_name'] = common_functions.remove_spec_char_from_list(df_date['Logbook_name'])

    return df_date

def extract_bait_v17(df_donnees):
    """
    Extraction des cases relatives au type d'appât utilisé
    selon la version du logbook v.17.6 de 2024

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

def extract_bait_v26(df_donnees):
    """
    Extraction des cases relatives au type d'appât utilisé
    selon la version du logbook v.18 de 2025

    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    df_bait = df_donnees.iloc[23:54, 40:41].copy()
    df_bait.columns = ['Bait']
    # Nettoyage
    df_bait['Bait'] = df_bait['Bait'].apply(
        lambda x: "".join(common_functions.remove_spec_char_from_list(x.strip()))
        if isinstance(x, str) and x.strip() != "" else x)
    return df_bait

def extract_positions(df_donnees, version):
    """
    Extraction des cases relatives aux données de position
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    
    if version == "ll_17.6":
        data = df_donnees.iloc[24:55, :7]
    elif version == "ll_26":
        data = df_donnees.iloc[23:54, :7]
    
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

def get_vessel_activity_topiaid_v17(startTimeStamp, allData):
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


def get_vessel_activity_topiaid_v26(df_donnees, allData):
    """
    Fonction qui prend en argument une heure de depart et qui donne un topiaID de VesselActivity en fonction du type et du contenu de l'entrée
    
    Args:
        startTimeStamp (date): information horaire - si type date alors Fishing operation, sinon on regarde le texte dans la cellule
        allData (json): données de références

    Returns:
        topiaID de l'activité détectée
    """
    if pd.isna(df_donnees):
        # If the vessel activity is not filled
        vessel_activity =  "fr.ird.referential.ll.common.VesselActivity#666#07"
    else :
        data_clean = df_donnees.strip().lower()
    
        if re.findall("cru", data_clean):
            vessel_activity = "fr.ird.referential.ll.common.VesselActivity#666#01"
            
        elif re.findall("fis", data_clean): 
            vessel_activity = "fr.ird.referential.ll.common.VesselActivity#1239832686138#0.1"

        elif re.findall("out", data_clean) or re.findall("ose", data_clean): 
            vessel_activity = "fr.ird.referential.ll.common.VesselActivity#666#04"

        elif re.findall("por", data_clean):
            vessel_activity = "fr.ird.referential.ll.common.VesselActivity#666#03"

        elif re.findall("tra", data_clean):
            vessel_activity = "fr.ird.referential.ll.common.VesselActivity#666#06"
        
        else:
            # OTHER
            vessel_activity = "fr.ird.referential.ll.common.VesselActivity#1239832686138#0.2"

    vessel_activities = allData["VesselActivity"]["longline"]

    # Chercher dans la liste
    vessel_activity_match = next(
        (v for v in vessel_activities if v["topiaId"] == vessel_activity),
        None  # valeur de retour si non trouvé
    )
    
    return vessel_activity_match["topiaId"], vessel_activity_match["label1"]

def extract_time(df_donnees, allData, version):
    """
    Extraction des cases relatives aux horaires des coups de pêche
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df: type horaire, sauf si le bateau est en mouvement
    """
    if version == "ll_17.6":
        day = df_donnees.iloc[24:55, 0]
        df_time = df_donnees.iloc[24:55, 7:8]
    elif version == "ll_26":
        day = df_donnees.iloc[23:54, 0]
        df_vesselactivity = df_donnees.iloc[23:54, 7:8]
        df_time = df_donnees.iloc[23:54, 8:9]
    
    colnames = ['Time']
    df_time.columns = colnames
    df_time['Time'] = df_time['Time'].apply(common_functions.convert_to_time_or_text)

    df_time.reset_index(drop=True, inplace=True)

    if version == "ll_17.6":
        vessel_activities = np.empty((len(day), 2), dtype=object)
        for ligne in range(len(day)):
            vessel_activity = get_vessel_activity_topiaid_v17(
                df_time.iloc[ligne]['Time'], allData)
            vessel_activities[ligne, 0] = vessel_activity[1]
            vessel_activities[ligne, 1] = vessel_activity[0]

    elif version == "ll_26":
        vessel_activities = np.empty((len(day), 2), dtype=object)
        for ligne in range(len(day)):
            vessel_activity = get_vessel_activity_topiaid_v26(df_vesselactivity.iloc[ligne].iloc[0], allData)          
            vessel_activities[ligne, 0] = vessel_activity[1]
            vessel_activities[ligne, 1] = vessel_activity[0]
        
    np_time = np.column_stack((day, df_time, vessel_activities ))
    df_time = pd.DataFrame(np_time, columns=['Day', 'Time', 'VesselActivity', 'VesselActivity_topiaId'])

    return df_time

def extract_temperature(df_donnees, version):
    """
    Extraction des cases relatives aux températures
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    if version == "ll_17.6":
        df_temp = df_donnees.iloc[24:55, 8:9]
    elif version == "ll_26":
        df_temp = df_donnees.iloc[23:54, 9:10]
    
    colnames = ['Temperature']
    df_temp.columns = colnames
    df_temp.reset_index(drop=True, inplace=True)
    return df_temp

def extract_fishing_effort(df_donnees, version):
    """
    Extraction des cases relatives aux efforts de pêche
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    if version == "ll_17.6":
        df_fishing_effort = df_donnees.iloc[24:55, [0, 9, 10, 11]].copy()
    elif version == "ll_26":
        df_fishing_effort = df_donnees.iloc[23:54, [0, 9, 10, 11]].copy()
    
    df_fishing_effort.columns = ['Day', 'Hooks per basket', 'Total hooks', 'Total lightsticks']
    
    try:
        df_fishing_effort['Total hooks / Hooks per basket'] = common_functions.convert_to_int(df_fishing_effort['Total hooks']) / common_functions.convert_to_int(df_fishing_effort['Hooks per basket'])
    except TypeError:
        df_fishing_effort['Total hooks / Hooks per basket'] = None
        
    df_fishing_effort.reset_index(drop=True, inplace=True)
    return df_fishing_effort

def extract_fish_p1_v17(df_donnees):
    """
    Extraction des cases relatives à ce qui a été pêché
    
    Args:
        df_donnees (df): excel p1

    Returns:
        df
    """
    df_fishes = df_donnees.iloc[24:55, 12:36]

    colnames = ['No. RET SBF', 'Kg RET SBF',
                'No. RET ALB', 'Kg RET ALB',
                'No. RET BET', 'Kg RET BET',
                'No. RET YFT', 'Kg RET YFT', 
                'No. RET SWO', 'Kg RET SWO',
                'No. RET MLS', 'Kg RET MLS',
                'No. RET BUM', 'Kg RET BUM',
                'No. RET BLM', 'Kg RET BLM',
                'No. RET SFA', 'Kg RET SFA',
                'No. RET SSP', 'Kg RET SSP', 
                'No. RET OIL', 'Kg RET OIL',
                'No. RET MZZ', 'Kg RET MZZ']
    
    df_fishes.columns = colnames
    df_fishes = df_fishes.map(common_functions.zero_if_empty)
    df_fishes.reset_index(drop=True, inplace=True)
    
    return df_fishes
    
    
def extract_bycatch_p2_v17(df_donnees):
    """
    Extraction des cases relatives à ce qui a été pêché mais accessoires    
    
    Args:
        df_donnees (df): excel p2

    Returns:
        df
    """
    df_bycatch = df_donnees.iloc[15:46, 1:39]

    colnames = ['No. RET FAL', 'Kg RET FAL',
                'No. ESC FAL', 'No. DIS FAL',
                'No. RET BSH', 'Kg RET BSH',
                'No. ESC BSH', 'No. DIS BSH',
                'No. RET MAK', 'Kg RET MAK',
                'No. ESC MAK', 'No. DIS MAK',
                'No. RET MSK', 'Kg RET MSK',
                'No. ESC MSK', 'No. DIS MSK', 
                'No. RET SPN', 'Kg RET SPN',
                'No. ESC SPN', 'No. DIS SPN', 
                'No. RET TIG', 'Kg RET TIG',
                'No. ESC TIG', 'No. DIS TIG', 
                'No. RET PSK', 'Kg RET PSK',
                'No. ESC PSK', 'No. DIS PSK',
                'No. ESC THR', 'No. DIS THR',
                'No. ESC OCS', 'No. DIS OCS', 
                'No. ESC MAM', 'No. DIS MAM', 
                'No. ESC SBD', 'No. DIS SBD',
                'No. ESC TTX', 'No. DIS TTX']
    df_bycatch.columns = colnames
    df_bycatch = df_bycatch.map(common_functions.zero_if_empty)
    df_bycatch.reset_index(drop=True, inplace=True)
    return df_bycatch

def extract_catches_v26(df_donnees, version):
    
    if version == "ll_17.6":
        df_fishes = df_donnees.iloc[22:55, 12:36]
    elif version == "ll_26":
        df_fishes = df_donnees.iloc[21:54, 13:39]
    
    df_fishes.columns = df_fishes.iloc[0]
    df_fishes = df_fishes.iloc[2:].reset_index(drop=True)

    fishes = []
    cols = list(df_fishes.columns)
                
    for _, row in df_fishes.iterrows():

        fishes_row = []  # 👈 liste pour UNE ligne

        for i in range(0, len(cols), 2):
            col_no = cols[i]
            col_kg = cols[i + 1]

            # récupérer le code espèce (SBF, ALB, BET…)
            species_match = re.search(r'\(([^)]+)\)', col_no)
            species_code = species_match.group(1) if species_match else None
            
            # specie_process = common_functions.remove_spec_char_from_list(col_kg)
            # utf_8 = col_kg.encode('utf-8')
            # specie_process = re.search(r'[^a-zA-Z]', utf_8)
            process_match = re.search(r'\b([A-Z]{2})\b\s*$', col_kg)
            specie_process = process_match.group(1) if process_match else None

            count = row[col_no]
            kg = row[col_kg]

            # normalisation des vides
            count = None if pd.isna(count) or count == '' or count == 0 else count
            kg = None if pd.isna(kg) or kg == '' or kg == 0 else kg

            # garder uniquement si au moins un est renseigné
            if count is None and kg is None:
                continue

            fishes_row.append({
                "species": species_code,
                "onBoardProcessing": specie_process,
                "catchFate" : 'RET',
                "discardHealthStatus": None,
                "count": count,
                "kg": kg
            })
        fishes.append(fishes_row)
        
    return fishes

def extract_bycatch_page2_v26(df_donnees):
    
    df_bycatches = df_donnees.iloc[11:46, 1:41]
    df_bycatches_columns = df_bycatches.iloc[0:2]

    df_bycatches = df_bycatches.iloc[4:].reset_index(drop=True)

    bycatches = []
    n_cols = df_bycatches.shape[1]
                
    for _, row in df_bycatches.iterrows():

        bycatches_row = [] 

        for i in range(0, n_cols, 4):
            col_species = df_bycatches_columns.iloc[0, i]
            col_process = df_bycatches_columns.iloc[1, i]
            
            # récupérer le code espèce (SBF, ALB, BET…)
            species_match = re.search(r'\(([^)]+)\)', col_species)
            species_code = species_match.group(1) if species_match else None
            
            # Récupérer le code de processing (HG, GG...)
            process_match = re.search(r'\b([A-Z]{2})\b\s*$', col_process)
            specie_process = process_match.group(1) if process_match else None

            count_ret = row.iloc[i]
            kg_ret = row.iloc[i+1]
            count_R_A = row.iloc[i+2]
            count_R_D = row.iloc[i+3]

            # normalisation des vides
            count_ret = None if pd.isna(count_ret) or count_ret == '' else count_ret
            kg_ret = None if pd.isna(kg_ret) or kg_ret == '' else kg_ret
            count_R_A = None if pd.isna(count_R_A) or count_R_A == '' else count_R_A
            count_R_D = None if pd.isna(count_R_D) or count_R_D == '' else count_R_D

            # garder uniquement si au moins un est renseigné
            if all(v in (None, 0, '') for v in [count_ret, kg_ret, count_R_A, count_R_D]):
                continue

            # ---------- RET ----------
            if count_ret is not None or kg_ret is not None:
                bycatches_row.append({
                    "species": species_code,
                    "onBoardProcessing": specie_process,
                    "catchFate": "RET",
                    "discardHealthStatus": None,
                    "count": count_ret,
                    "kg": kg_ret
                })

            # ---------- DIS / A ----------
            if count_R_A is not None:
                bycatches_row.append({
                    "species": species_code,
                    "onBoardProcessing": specie_process,
                    "catchFate": "DIS",
                    "discardHealthStatus": "A",
                    "count": count_R_A,
                    "kg": None
                })

            # ---------- DIS / D ----------
            if count_R_D is not None:
                bycatches_row.append({
                    "species": species_code,
                    "onBoardProcessing": specie_process,
                    "catchFate": "DIS",
                    "discardHealthStatus": "D",
                    "count": count_R_D,
                    "kg": None
                })

        bycatches.append(bycatches_row)
        
    return bycatches

def extract_bycatch_page3_v26(df_donnees, df_ref):
    """
    Extraction des captures accessoires page 3 du logbook version 2026.
    
    Args:
        df_donnees (df): feuille page 3
        df_ref (df): feuille page 4 (références)
        
    Returns:
        list of dict: captures par ligne
    """

    # -------------------------
    # Préparation des données
    # -------------------------
    df_bycatches = df_donnees.iloc[11:46, 1:27]
    df_bycatches_columns = df_bycatches.iloc[0:2]
    df_bycatches = df_bycatches.iloc[4:].reset_index(drop=True)

    df_ref_bycatch = ref_table_bycatch(df_ref)
    df_ref_bycatch = df_ref_bycatch.rename(columns={'CODE 代碼': 'CODE', 'NAME_EN 英文名': 'NAME_EN'})
    df_ref_bycatch['NAME_EN'] = df_ref_bycatch['NAME_EN'].str.strip()

    bycatches = []
    n_cols = df_bycatches.shape[1]

    def clean(v):
        return None if pd.isna(v) or v in ('', 0) else v

    for _, row in df_bycatches.iterrows():

        bycatches_row = []

        # -------------------------
        # Colonnes SKH : RET + DIS A / DIS D
        # -------------------------
        col_species = df_bycatches_columns.iloc[0, 0]
        col_process = df_bycatches_columns.iloc[1, 0]

        species_match = re.search(r'\(([^)]+)\)', str(col_species))
        species_code = species_match.group(1) if species_match else col_species

        process_match = re.search(r'\b([A-Z]{2})\b\s*$', str(col_process))
        specie_process = process_match.group(1) if process_match else None

        count_ret = clean(row.iloc[0])
        kg_ret = clean(row.iloc[1])
        count_DIS_A = clean(row.iloc[2])
        count_DIS_D = clean(row.iloc[3])

        if count_ret is not None or kg_ret is not None:
            bycatches_row.append({
                "species": species_code,
                "onBoardProcessing": specie_process,
                "catchFate": "RET",
                "discardHealthStatus": None,
                "count": count_ret,
                "kg": kg_ret
            })

        if count_DIS_A is not None:
            bycatches_row.append({
                "species": species_code,
                "onBoardProcessing": specie_process,
                "catchFate": "DIS",
                "discardHealthStatus": "A",
                "count": count_DIS_A,
                "kg": None
            })

        if count_DIS_D is not None:
            bycatches_row.append({
                "species": species_code,
                "onBoardProcessing": specie_process,
                "catchFate": "DIS",
                "discardHealthStatus": "D",
                "count": count_DIS_D,
                "kg": None
            })

        # -------------------------
        # Colonnes : DIS A / DIS D
        # -------------------------
        i = 4

        while i < 12:
            
            col_species = df_bycatches_columns.iloc[0, i]
            col_process = df_bycatches_columns.iloc[1, i]

            species_match = re.search(r'\(([^)]+)\)', str(col_species))
            species_code = species_match.group(1) if species_match else col_species

            process_match = re.search(r'\b([A-Z]{2})\b\s*$', str(col_process))
            specie_process = process_match.group(1) if process_match else None

            v0 = clean(row.iloc[i])
            v1 = clean(row.iloc[i + 1]) if i + 1 < n_cols else None

            if v0 is not None:
                bycatches_row.append({
                    "species": species_code,
                    "onBoardProcessing": specie_process,
                    "catchFate": "DIS",
                    "discardHealthStatus": "A",
                    "count": v0,
                    "kg": None
                })

            if v1 is not None:
                bycatches_row.append({
                    "species": species_code,
                    "onBoardProcessing": specie_process,
                    "catchFate": "DIS",
                    "discardHealthStatus": "D",
                    "count": v1,
                    "kg": None
                })

            i += 2

        # -------------------------
        # Colonnes : species (str), DIS A, DIS D
        # -------------------------
        i = 12
        while i < 24:
            specie_name = row.iloc[i]
            count_RA = clean(row.iloc[i + 1]) if i + 1 < n_cols else None
            count_RD = clean(row.iloc[i + 2]) if i + 2 < n_cols else None

            if pd.notna(specie_name) and isinstance(specie_name, str):
                if len(specie_name) >= 4:
                    species_code = df_ref_bycatch.loc[df_ref_bycatch['NAME_EN'] == specie_name, 'CODE'].values[0]
                else:
                    species_code=specie_name
                
                if count_RA is not None:
                    bycatches_row.append({
                        "species": species_code,
                        "onBoardProcessing": None,
                        "catchFate": "DIS",
                        "discardHealthStatus": "A",
                        "count": count_RA,
                        "kg": None
                    })

                if count_RD is not None:
                    bycatches_row.append({
                        "species": species_code,
                        "onBoardProcessing": None,
                        "catchFate": "DIS",
                        "discardHealthStatus": "D",
                        "count": count_RD,
                        "kg": None
                    })

            i += 3
        
        
        # -------------------------
        # LAST Colonnes : species == WHALE SHARK, DIS A, DIS D
        # -------------------------
        i = 24
        while i < n_cols:
            species_code = "RHN"
            count_RA = clean(row.iloc[i + 1]) if i + 1 < n_cols else None
            count_RD = clean(row.iloc[i + 2]) if i + 2 < n_cols else None

            if count_RA is not None:
                bycatches_row.append({
                    "species": species_code,
                    "onBoardProcessing": None,
                    "catchFate": "DIS",
                    "discardHealthStatus": "A",
                    "count": count_RA,
                    "kg": None
                })

            if count_RD is not None:
                bycatches_row.append({
                    "species": species_code,
                    "onBoardProcessing": None,
                    "catchFate": "DIS",
                    "discardHealthStatus": "D",
                    "count": count_RD,
                    "kg": None
                })

            i += 2

        bycatches.append(bycatches_row)

    return bycatches


def extract_seabirds_ref(df_donnees):
    """
    Extraction des cases de références relatives aux espèces d'oiseaux marins
    
    Args:
        df_donnees (df): excel p4 du logbook version 2026

    Returns:
        df
    """
    df_seabirds = df_donnees.iloc[2:34, 5:8].copy()
    # La première ligne de df_seabirds devient le nom des colonnes
    df_seabirds.columns = df_seabirds.iloc[0]

    # Supprimer la première ligne 
    df_seabirds = df_seabirds[1:].reset_index(drop=True)

    # Optionnel : nettoyer les noms de colonnes
    df_seabirds.columns = [str(c).strip() for c in df_seabirds.columns]

    return df_seabirds

def extract_marineturtles_ref(df_donnees):
    """
    Extraction des cases de références relatives aux espèces de tortues marines
    
    Args:
        df_donnees (df): excel p4 du logbook version 2026

    Returns:
        df
    """
    df_marineturtles = df_donnees.iloc[43:51, 1:4].copy()
    # La première ligne de df_seabirds devient le nom des colonnes
    df_marineturtles.columns = df_marineturtles.iloc[0]

    # Supprimer la première ligne 
    df_marineturtles = df_marineturtles[1:].reset_index(drop=True)

    return df_marineturtles

def extract_rays_ref(df_donnees):
    """
    Extraction des cases de références relatives aux espèces de raies
    
    Args:
        df_donnees (df): excel p4 du logbook version 2026

    Returns:
        df
    """
    df_rays = df_donnees.iloc[53:70, 1:4].copy()
    # La première ligne de df_rays devient le nom des colonnes
    df_rays.columns = df_rays.iloc[0]

    # Supprimer la première ligne 
    df_rays = df_rays[1:].reset_index(drop=True)

    return df_rays

def extract_cetaceans_ref(df_donnees):
    """
    Extraction des cases de références relatives aux espèces de cetacés
    
    Args:
        df_donnees (df): excel p4 du logbook version 2026

    Returns:
        df
    """
    df_cetaceans = df_donnees.iloc[36:82, 5:8].copy()
    # La première ligne de df_cetaceans devient le nom des colonnes
    df_cetaceans.columns = df_cetaceans.iloc[0]

    # Supprimer la première ligne 
    df_cetaceans = df_cetaceans[1:].reset_index(drop=True)

    return df_cetaceans

def extract_baits_ref(df_donnees):
    """
    Extraction des cases de références relatives aux appâts
    
    Args:
        df_donnees (df): excel p4 du logbook version 2026

    Returns:
        df
    """
    df_ref_baits = df_donnees.iloc[2:7, 9:11].copy()
    # La première ligne de df_ref_baits devient le nom des colonnes
    df_ref_baits.columns = df_ref_baits.iloc[0]

    # Supprimer la première ligne 
    df_ref_baits = df_ref_baits[1:].reset_index(drop=True)
    df_ref_baits = df_ref_baits.rename(columns={'CODE 代碼': 'CODE'})
    
    return df_ref_baits

def ref_table_bycatch(df_donnees):
    """
    Extraction des cases de références relatives aux captures accessoires
    
    Args:
        df_donnees (df): excel p4 du logbook version 2026

    Returns:
        df
    """
    df_ref_bycatch = pd.concat([
            extract_cetaceans_ref(df_donnees),
            extract_rays_ref(df_donnees),
            extract_marineturtles_ref(df_donnees),
            extract_seabirds_ref(df_donnees)
        ], ignore_index=True)

    return df_ref_bycatch

def extract_material_ref(df_donnees):
    """
    Extraction des cases de références relatives aux matériels
    
    Args:
        df_donnees (df): excel p4 du logbook version 2026

    Returns:
        df
    """
    df_ref_materials = df_donnees.iloc[23:28, 9:11].copy()
    # La première ligne de df_ref_materials devient le nom des colonnes
    df_ref_materials.columns = df_ref_materials.iloc[0]

    # Supprimer la première ligne 
    df_ref_materials = df_ref_materials[1:].reset_index(drop=True)
    df_ref_materials = df_ref_materials.rename(columns={'CODE 代碼': 'CODE'})
    df_ref_materials['CODE'] = df_ref_materials['CODE'].str.strip()
    
    mappingLine_v26 = {
        "N": "MUN",
        "NB": "BRL",
        "NM": "MON",
        "OTH": "UNK"}

    df_ref_materials["Code_v26"] = df_ref_materials["CODE"].map(mappingLine_v26)

    return df_ref_materials
