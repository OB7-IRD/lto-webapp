# import os
import json
# import warnings
import palangre_syc.api
from palangre_syc.views import *

def get_captain_topiaID(df_donnees_p1, data_common):
    """
    Fonction qui propose le topiaID associé au capitaine du logbook 
    (ou inconnu is non présent dans les données de référence)

    Args:
        df_donnees_p1 (dataframe): page 1 du doc excel
        data_common (json): Données de références 'common'

    Returns:
        _type_: topiaID du capitaine présenté dans le logbook
    """
    for captain in data_common['content']['fr.ird.observe.entities.referential.common.Person']:

        captain_Logbook = palangre_syc.views.extract_cruiseInfo_LL(df_donnees_p1).loc[palangre_syc.views.extract_cruiseInfo_LL(
            df_donnees_p1)['Logbook_name'] == 'Captain', 'Value'].values[0]
        captain_json = captain['firstName'] + ' ' + captain['lastName']
        if captain_Logbook == captain_json:
            return captain['topiaId']
        else:
            captain_Logbook = '[inconnu] [inconnu]'
            if captain_Logbook == captain_json:
                return captain['topiaId']
    return None


def get_lb_operator_topiaID(df_donnees_p1, data_common):
    """
    Fonction qui propose le topiaID de la personne qui a saisi les données du logbook (ou inconnu is non présent dans les données de référence)

    Args:
        df_donnees_p1 (dataframe): page 1 du doc excel
        data_common (json): Données de références 'common'

    Returns:
        _type_: topiaID de l'opérateur 
    """
    for person in data_common['content']['fr.ird.observe.entities.referential.common.Person']:

        reported_Logbook = palangre_syc.views.extract_reportInfo_LL(df_donnees_p1).loc[palangre_syc.views.extract_reportInfo_LL(
            df_donnees_p1)['Logbook_name'] == 'Person reported', 'Value'].values[0]
        reported_json = person['firstName'] + ' ' + person['lastName']
        if reported_Logbook == reported_json:
            return person['topiaId']
        else:
            reported_Logbook = '[inconnu] [inconnu]'
            if reported_Logbook == reported_json:
                return person['topiaId']
    return None


def get_vessel_topiaID(df_donnees_p1, data_common):
    """
    Fonction qui propose le topiaId du navire cité dans le logbook à partir de son 'nationlId' s'il existe 

    Args:
        df_donnees_p1 (dataframe): page 1 du doc excel
        data_common (json): Données de références 'common'

    Returns:
        _type_: topiaID du navire (vessel)
    """
    vessel_Logbook = palangre_syc.views.extract_vesselInfo_LL(df_donnees_p1).loc[palangre_syc.views.extract_vesselInfo_LL(
        df_donnees_p1)['Logbook_name'] == 'Official Number', 'Value'].values[0]
    for vessel in data_common["content"]["fr.ird.observe.entities.referential.common.Vessel"]:
        if 'nationalId' in vessel:
            vessel_json = vessel['nationalId']
            if vessel_Logbook == vessel_json:
                return vessel['topiaId']

    # il faudrait faire un message qui dit de vérifier si le bateau est bien existant et présent dans la base
    # si 'nationalId' n'est pas dans vessel
    return None


def get_BaitType_topiaId(row, data_ll):
    """
    Fonction qui propose le topiaId de l'appat coché dans le logbook 

    Args:
        row (dataframe): nom de l'appât 
        data_ll (json):  Données de références 'longliners'

    Returns:
        str: topiaID de l'appât utilisé
    """
    BaitTypes = data_ll["content"]["fr.ird.observe.entities.referential.ll.common.BaitType"]
    Bait_logbook = row['Logbook_name']
    for BaitType in BaitTypes:
        if BaitType.get("label1")[:len(Bait_logbook)] == Bait_logbook:
            return BaitType["topiaId"]


def get_Species_topiaID(FAO_code_logbook, data_common):
    """
    Fonction qui propose le topiaId pour une espèce à partir de son code FAO (saisi manuellement dans la trascription du excel)

    Args:
        FAO_code_logbook (_type_): Code FAO (3 caractères) extrait du datatable de prises créé depuis la page 1 et 2
        data_common (json): Données de références 'common'

    Returns:
        str: topiaID de l'espèce demandée
    """

    Species = data_common["content"]["fr.ird.observe.entities.referential.common.Species"]
    for Specie in Species:
        lambda Specie: 'fao_code' in Specie
        if FAO_code_logbook == Specie.get("faoCode"):
            return Specie["topiaId"]
        # On part du principe que si le code fao n'est pas exactement trouvé, c'est qu'il s'agit d'une espèce non identifié
        elif Specie.get("faoCode") == "XXX*":
            return Specie["topiaId"]
    return None


def get_catchFate_topiaID(catchFate_logbook, data_ll):
    """
    Fonction qui propose le topiaId du devenir de l'espèce (associé manuellement à l'espèce dans la trascription du excel)

    Args:
        catchFate_logbook (str): Code catchFate (3 caractères) extrait du datatable de prises créé depuis la page 1 et 2
        data_ll (json): Données de références 'longliners'

    Returns:
        str: topiaID du devenir de l'espèce demandée
    """

    Fates = data_ll["content"]["fr.ird.observe.entities.referential.ll.common.CatchFate"]
    for catchFate in Fates:
        if 'code' in catchFate:
            if catchFate.get("code") == catchFate_logbook:
                return catchFate["topiaId"]
        else :
            return None


# Opimisation éventuelle : ajouter unparamètre qui permettrait de distinguer les fish des bycatch
# notamment si les by catch son relachées A alive ou D dead

def construction_catch_table(fish_file):
    """

    Args:
        fish_file (dataframe): Issu des fonction d'extraction propre à chaque espèce ou groupe d'espèce

    Returns:
        dataframe: Construction d'un df avec chaque code FAO et le catchfate associée en lignes
    """
    df_catches = pd.DataFrame(
        columns=['FAO_code', 'catchFate', 'count', 'totalWeight'])

    # On récupère les données des colonnes de FAO et catchFate
    for col in fish_file.columns:
        FAO_code = col[-3:]
        catchFate = col[-7:-4]
        df_catches.loc[len(df_catches)] = {
            'FAO_code': FAO_code, 'catchFate': catchFate}

    # On supprime les doublons
    df_catches = df_catches.drop_duplicates()
    df_catches.reset_index(drop=True, inplace=True)

    return df_catches

# a voir si c'est pertinent en terme de gain de temps de découper la fonction ici en 2
# on pourrait avoir une fonctionn qui gère les lignes issues des noms de colonnes
# et une seconde fonction qui remplirait les lignes count et totalWeight en allant chercher les infos dans le excel


def create_catch_table_fish_perday(fish_file, row_number):
    """
    Args:
        fish_file (datatable): issu des extraction, donc un datatable par groupe d'espèce
        row_number (int): ligne (ou un jour de pêche) à extraire

    Returns:
        dataframe: par type de poisson pêché et par jour de pêche de 4 colonnes 
    Ce dataframe contient les champs obligatoires à remplir dans la table 'catch' de Observe
    """

    df_catches = construction_catch_table(fish_file)

    # On rempli la suite du dataframe pour count et totalWeight (pour une ligne donnée)
    for index, row in df_catches.iterrows():
        col_end_name = row['catchFate'] + ' ' + row['FAO_code']
        for col in fish_file.columns:
            if col[-7:] == col_end_name:
                if col[:2] == 'No':
                    fish_file_colname = 'No' + ' ' + col_end_name
                    count = fish_file.loc[row_number, fish_file_colname]
                    df_catches.loc[index, 'count'] = count
                    # df_catches.loc[index, 'count'] = int(df_catches.loc[index, 'count'])

                if col[:2] == 'Kg':
                    fish_file_colname = 'Kg' + ' ' + col_end_name
                    totalWeight = fish_file.loc[row_number, fish_file_colname]
                    df_catches.loc[index, 'totalWeight'] = totalWeight
                    # df_catches.loc[index, 'totalWeight'] = int(df_catches.loc[index, 'totalWeight'])

                # a voir si on veut des Nan car il n'y a pas de donnée ou des 0
                else:
                    df_catches.loc[index, 'totalWeight'] = int(0)

    return df_catches


def create_catch_table_fishes(df_donnees_p1, df_donnees_p2, row_number):
    """

    Args:
        df_donnees_p1 (dataframe): page 1 du doc excel
        df_donnees_p2 (dataframe): page 2 du doc excel
        row_number (int): ligne ou jour du set

    Returns:
        dataframe: avec les prises réalisées pour une journée de pêche (code FAO, catchFate, nombre de prise et Poids tot)
    """
    liste_fct_extraction = [palangre_syc.views.extract_tunas(df_donnees_p1),
                            palangre_syc.views.extract_billfishes(
                                df_donnees_p1),
                            palangre_syc.views.extract_otherfish(
                                df_donnees_p1),
                            palangre_syc.views.extract_sharksFAL(
                                df_donnees_p2),
                            palangre_syc.views.extract_sharksBSH(
                                df_donnees_p2),
                            palangre_syc.views.extract_sharksMAK(
                                df_donnees_p2),
                            palangre_syc.views.extract_sharksSPN(
                                df_donnees_p2),
                            palangre_syc.views.extract_sharksTIG(
                                df_donnees_p2),
                            palangre_syc.views.extract_sharksPSK(
                                df_donnees_p2),
                            palangre_syc.views.extract_sharksTHR(
                                df_donnees_p2),
                            palangre_syc.views.extract_sharksOCS(
                                df_donnees_p2),
                            palangre_syc.views.extract_mammals(df_donnees_p2),
                            palangre_syc.views.extract_seabird(df_donnees_p2),
                            palangre_syc.views.extract_turtles(df_donnees_p2)]

    df_catches = pd.DataFrame(
        columns=['FAO_code', 'catchFate', 'count', 'totalWeight'])

    for fish_file in liste_fct_extraction:
        df_per_extraction = create_catch_table_fish_perday(
            fish_file, row_number)
        df_catches = pd.concat(
            [df_catches, df_per_extraction], ignore_index=True)

    # Tester si les colonnes 'count' et 'totalWeight' contiennent des zéros
    not_catch = df_catches[(df_catches['count'] == 0) &
                           (df_catches['totalWeight'] == 0)]
    # Supprimer les lignes qui contiennent des zéros dans ces colonnes
    df_catches = df_catches.drop(not_catch.index)
    df_catches.reset_index(drop=True, inplace=True)

    return df_catches

# TopType et tracelineType sont unknown


def create_branchelinesComposition(df_donnees_p1):
    """
    Fonction de construction du json pour les branchlineComposition

    Args:
        df_donnees_p1 (dataframe): page 1 du doc excel

    Returns:
        _type_: le json rempli à partir des infos de mon logbook
    """
    branchlinesComposition = [{
        'homeId': None,
        'length': palangre_syc.views.extract_gearInfo_LL(df_donnees_p1).loc[palangre_syc.views.extract_gearInfo_LL(df_donnees_p1)['Logbook_name'] == 'Set Line length m', 'Value'].values[0],
        'proportion': None,
        'tracelineLength': None,
        'topType': "fr.ird.referential.ll.common.LineType#1239832686157#0.9",
        'tracelineType': "fr.ird.referential.ll.common.LineType#1239832686157#0.9",
    }]
    return branchlinesComposition


def create_BaitComposition(bait_datatable, data_ll):
    """
    Fonction de construction du json pour les BaitComposition

    Args:
        bait_datatable (datatable): datatable non vide 'Baits' construite in views.py
        data_ll (json):  Données de références 'longliners'

    Returns:
        _type_: le json rempli à partir des infos de mon logbook
    """
    baits_used = bait_datatable.loc[bait_datatable['Value'] != "None"]
    total_baits = len(baits_used)
    MultipleBaits = []

    for index, row in baits_used.iterrows():
        BaitsComposition = {
            "homeId": None,
            "proportion": 100/total_baits,
            "individualSize": None,
            "individualWeight": None,
            "baitSettingStatus": None,
            "baitType": get_BaitType_topiaId(row, data_ll),
        }
        MultipleBaits.append(BaitsComposition)

    return MultipleBaits


def create_FloatlineComposition(df_gear):
    """
    Fonction de construction du json pour les FloatlineComposition

    Args:
        df_donnees_p1 (dataframe): page 1 du doc excel

    Returns:
        _type_: le json rempli à partir des infos de mon logbook
    """
    FloatlinesComposition = [{
        "homeId": None,
        # "length": palangre_syc.views.extract_gearInfo_LL(df_donnees_p1).loc[palangre_syc.views.extract_gearInfo_LL(df_donnees_p1)['Logbook_name'] == 'Floatline length m', 'Value'].values[0],
        "length": df_gear.loc[df_gear['Logbook_name'] == 'Floatline length m', 'Value'].values[0],
        "proportion": 100,
        "lineType": "fr.ird.referential.ll.common.LineType#1239832686157#0.9"
    }]
    return FloatlinesComposition

# peut etre ajouter le healthStatus


def create_catches(datatable, data_common, data_ll):
    """
    Fonction de construction du json pour les catches

    Args:
        datatable (datatable): datatable créé pour une journée / un set
        data_common (json):  Données de références 'common'
        data_ll (json):  Données de références 'longliners'

    Returns:
        _type_: le json rempli à partir des infos de mon logbook
    """
    MultipleCatches = []
    for n_ligne_datatable in range(len(datatable)):
        catches = {"homeId": None, }
        if get_Species_topiaID(datatable.loc[n_ligne_datatable, 'FAO_code'], data_common) == 'fr.ird.referential.common.Species#1433499266610#0.696541526820511' or get_Species_topiaID(datatable.loc[n_ligne_datatable, 'FAO_code'], data_common) == 'fr.ird.referential.common.Species#1239832685020#0.7691470969492022':
            catches.update({"comment": "Other fish non specified", })
        else:
            catches.update({"comment": None, })
        catches.update({"count": datatable.loc[n_ligne_datatable, 'count'],
                        "totalWeight": datatable.loc[n_ligne_datatable, 'totalWeight'],
                        "hookWhenDiscarded": None,
                        "depredated": None,
                        "beatDiameter": None,
                        "photoReferences": None,
                        "number": None,
                        "acquisitionMode": None,
                        "countDepredated": None,
                        "depredatedProportion": None,
                        "tagNumber": None,
                        "catchFate": get_catchFate_topiaID(datatable.loc[n_ligne_datatable, 'catchFate'], data_ll),
                        "discardHealthStatus": None,
                        "species": get_Species_topiaID(datatable.loc[n_ligne_datatable, 'FAO_code'], data_common),
                        "predator": [],
                        "catchHealthStatus": None,
                        "onBoardProcessing": None,
                        "weightMeasureMethod": None
                        })
        MultipleCatches.append(catches)
    return MultipleCatches


def create_starttimestamp(df_donnees_p1, data_ll, index_day, need_hour=bool):
    """ Fonction qui permet d'avoir le bon format de date-time pour envoyer le json

    Args:
        df_donnees_p1 (_type_): ma page excel 1
        data_ll (json):  Données de références 'longliners'
        index_day (int): le numero de la ligne de mon datatable
        need_hour (bool) : si true - on va chercher l'heure correspondante dans le datatable, 
        si false - on ajoute '00:00:00' cad que le bateau n'est pas en train de pêcher donc il nous faut une horaire juste pour convenir au format demandé

    Returns:
        _type_: la datetime au format qui permet l'insersion dans la bdd
    """
    if need_hour is True:
        time_ = palangre_syc.views.extract_time(
            df_donnees_p1, data_ll).loc[index_day, 'Time']
    else:
        time_ = '00:00:00'

    date_formated = '{}-{:02}-{:02}T{}.000Z'.format(
        palangre_syc.views.extract_logbookDate_LL(df_donnees_p1).loc[palangre_syc.views.extract_logbookDate_LL(
            df_donnees_p1)['Logbook_name'] == 'Year', 'Value'].values[0],
        palangre_syc.views.extract_logbookDate_LL(df_donnees_p1).loc[palangre_syc.views.extract_logbookDate_LL(
            df_donnees_p1)['Logbook_name'] == 'Month', 'Value'].values[0],
        palangre_syc.views.extract_time(
            df_donnees_p1, data_ll).loc[index_day, 'Day'],
        time_)
    return date_formated

def create_starttimestamp_from_fieldDate(date):
    """ Fonction qui permet d'avoir le bon format de date-time pour envoyer le json

    Args: 
        date: issue du input 
        
    Returns:
        datetime: pour stratDate et endDAte
    """
    date_formated = '{}-{:02}-{:02}T{}.000Z'.format(
        date[:4],
        date[5:7],
        date[-2:],
        '00:00:00')
    return date_formated

def search_date_into_json(json_previoustrip, date_to_look_for):
    ''' fonction qui recherche si la 1ere date du excel est deja saisie ou non dans le json'''
    
    for content in json_previoustrip:
        for activity in content['activityLogbook'] :
            start_time = activity.get('startTimeStamp')
            print("date trouvée dans le json : ", start_time)
            print("date de mon excel ", date_to_look_for)
            # print("activity['settingStartTimeStamp'] == ", activity["activityLogbook"]["settingStartTimeStamp"])
            if start_time and start_time.startswith(date_to_look_for) :
                print("False : erreur pour l'utilisateur")
                return True
            else : 
                print("True : donc mon logbook est nouveau et peut être ajouté au précédent")

    return False
            
    

def create_activity_and_set(df_donnees_p1, df_donnees_p2, data_common, data_ll, DAYS_IN_A_MONTH):
    # days_in_a_month = len(extract_positions(df_donnees_p1))
    # MultipleSet = []
    if isinstance(palangre_syc.views.extract_gearInfo_LL(df_donnees_p1), tuple) : 
        df_gear, _ = palangre_syc.views.extract_gearInfo_LL(df_donnees_p1)
    else:
        df_gear = palangre_syc.views.extract_gearInfo_LL(df_donnees_p1)
        
    # mais pour l'instant on ne traite pas cette info anyways 
    if isinstance(palangre_syc.views.extract_lineMaterial_LL(df_donnees_p1), tuple) : 
        df_line, _ = palangre_syc.views.extract_lineMaterial_LL(df_donnees_p1)
    else:
        df_line = palangre_syc.views.extract_lineMaterial_LL(df_donnees_p1)
      
        
        
    MultipleActivity = []
    for i in range(0, DAYS_IN_A_MONTH):
        set = {
            'homeId': None,
            'comment': None,
            'number': None,
            'basketsPerSectionCount': None,
            'branchlinesPerBasketCount': None,
            'totalSectionsCount': None,
            # 'totalBasketsCount' : extract_fishingEffort(file_path).loc[extract_fishingEffort(file_path)['Day'] == index + 1, 'Hooks'].values[0],
            # Lui je sais pas si la valeur correspond bien enft
            'totalBasketsCount': palangre_syc.views.extract_fishingEffort(df_donnees_p1).loc[i, 'Total hooks / Hooks per basket'],
            'totalHooksCount': palangre_syc.views.extract_fishingEffort(df_donnees_p1).loc[i, 'Total hooks'],
            'totalLightsticksCount': palangre_syc.views.extract_fishingEffort(df_donnees_p1).loc[i, 'Total lightsticks'],
            # 'totalLightsticksCount': None,
            'weightedSnap': False,
            'snapWeight': None,
            'weightedSwivel': False,
            'swivelWeight': None,
            'timeBetweenHooks': None,
            'shooterUsed': False,
            'shooterSpeed': None,
            'maxDepthTargeted': None, }

        set.update({'settingStartTimeStamp': create_starttimestamp(
            df_donnees_p1, data_ll, index_day=i, need_hour=True)})

        set.update({'settingStartLatitude': palangre_syc.views.extract_positions(df_donnees_p1).loc[i, 'Latitude'],
                    'settingStartLongitude': palangre_syc.views.extract_positions(df_donnees_p1).loc[i, 'Longitude'],
                    'settingEndTimeStamp': None,
                    'settingEndLatitude': None,
                    'settingEndLongitude': None,
                    'settingVesselSpeed': None,
                    'haulingDirectionSameAsSetting': None,
                    'haulingStartTimeStamp': None,
                    'haulingStartLatitude': None,
                    'haulingStartLongitude': None,
                    'haulingEndTimeStamp': None,
                    'haulingEndLatitude': None,
                    'haulingEndLongitude': None,
                    'haulingBreaks': None,
                    'monitored': False,
                    # En fait "totalLineLength" serait de plusierus km, ce qui ne correspond pas avec le champ "Set Line length m"
                    # 'totalLineLength' : extract_gearInfo_LL(df_donnees_p1).loc[extract_gearInfo_LL(df_donnees_p1)['Logbook_name'] == 'Set Line length m', 'Value'].values[0],
                    'totalLineLength': None,
                    'basketLineLength': None,
                    'lengthBetweenBranchlines': df_gear.loc[df_gear['Logbook_name'] == 'Length between branches m', 'Value'].values[0]
                    # palangre_syc.views.extract_gearInfo_LL(df_donnees_p1).loc[palangre_syc.views.extract_gearInfo_LL(df_donnees_p1)['Logbook_name'] == 'Length between branches m', 'Value'].values[0]
                    })

        bait_datatable = palangre_syc.views.extract_bait_LL(df_donnees_p1)
        set.update({'baitsComposition': create_BaitComposition(
            bait_datatable, data_ll), })

        set.update({'floatlinesComposition': create_FloatlineComposition(df_gear),
                    'hooksComposition': [], 
                    'settingShape': None, })

        datatable = create_catch_table_fishes(
            df_donnees_p1, df_donnees_p2, row_number=i)
        set.update({
            'catches': create_catches(datatable, data_common, data_ll),
            'lineType': None,
            'lightsticksUsed': False,
            'lightsticksType': None,
            'lightsticksColor': None,
            'mitigationType': [],
            'branchlinesComposition': []
        })
        # MultipleSet.append(set)

        activity = {
            'homeId': None,
            'comment': None, }
        if palangre_syc.views.extract_time(df_donnees_p1, data_ll).loc[i, 'VesselActivity'] == 'fr.ird.referential.ll.common.VesselActivity#1239832686138#0.1':
            activity.update({'startTimeStamp': create_starttimestamp(
                df_donnees_p1, data_ll, index_day=i, need_hour=True)})
        else:
            activity.update({'startTimeStamp': create_starttimestamp(df_donnees_p1, data_ll, index_day=i, need_hour=False)                             # 'startTimeStamp' : '2022-07-26T00:00:00.000Z'
                             , })

        activity.update({'endTimeStamp': None,
                         'latitude': palangre_syc.views.extract_positions(df_donnees_p1).loc[i, 'Latitude'],
                         'longitude': palangre_syc.views.extract_positions(df_donnees_p1).loc[i, 'Longitude'],
                         'seaSurfaceTemperature': palangre_syc.views.extract_temperature(df_donnees_p1).loc[i, 'Température'],
                         'wind': None,
                         'windDirection': None,
                         'currentSpeed': None,
                         'currentDirection': None,
                         'vesselActivity': palangre_syc.views.extract_time(df_donnees_p1, data_ll).loc[i, 'VesselActivity'],
                         'dataQuality': None,
                         'fpaZone': None,
                         'relatedObservedActivity': None,
                         # 'set' : MultipleSet,
                         })

        if activity.get('vesselActivity') == 'fr.ird.referential.ll.common.VesselActivity#1239832686138#0.1':
            activity.update({'set': set, })
        else:
            activity.update({
                'set': None,
                'sample': None
            })

        MultipleActivity.append(activity)

    return MultipleActivity


def create_trip(df_donnees_p1, MultipleActivity, data_common, apply_conf, context):
    # Dans le trip on a fixé :
    # tripType = Marée de pêche commerciale
    # observer = unknown car non présent
    # startDate et endDate sont entrées en dur aussi

    # species semble être TargetSpecies - a voir si on développe

    trip = {
        'homeId': None,}

    if apply_conf['startDate'] != None :
        trip.update({'startDate': create_starttimestamp_from_fieldDate(apply_conf['startDate']), })
    else : 
        trip.update({'startDate': context['startDate'], })
        
    trip.update({
        'endDate': create_starttimestamp_from_fieldDate(apply_conf['endDate']),
        'noOfCrewMembers': palangre_syc.views.extract_cruiseInfo_LL(df_donnees_p1).loc[palangre_syc.views.extract_cruiseInfo_LL(df_donnees_p1)['Logbook_name'] == 'No Of Crew', 'Value'].values[0],
        'ersId': None,
        'gearUseFeatures': None,
        'activityObs': None,
        'activityLogbook': MultipleActivity,
        'landing': None,
        'sample': None,
        'tripType': 'fr.ird.referential.ll.common.TripType#1464000000000#02',
        'observationMethod': None,
        'observer': 'fr.ird.referential.common.Person#1254317601353#0.6617065204572095',
        'vessel': get_vessel_topiaID(df_donnees_p1, data_common),
        'observationsProgram': None,
        'logbookProgram': apply_conf['programme'],
        'captain': get_captain_topiaID(df_donnees_p1, data_common),
        'observationsDataEntryOperator': None,
        'logbookDataEntryOperator': get_lb_operator_topiaID(df_donnees_p1, data_common),
        'sampleDataEntryOperator': None,
        'landingDataEntryOperator': None,
        'ocean': apply_conf['ocean'],})
    
    if apply_conf['depPort'] != None :
        trip.update({'departureHarbour': apply_conf['depPort'], })
    else : 
        trip.update({'departureHarbour': context['depPort_topiaid'], })
        
    
    trip.update({ 
        'landingHarbour': apply_conf['endPort'],
        'observationsDataQuality': None,
        'logbookDataQuality': None,
        'generalComment': None,
        'observationsComment': None,
        'logbookComment': None,
        'species': None,
        'observationsAvailability': False,
        'logbookAvailability': True,
    })
    return trip



def add_activity_and_set_to_trip(json_previoustrip, MultipleActivity):

    json_previoustrip['content'].append(MultipleActivity)
    
    return json.dumps(json_previoustrip, indent=2)
    
    
    return trip




def pretty_print(json_data, file="sample.json", mode="a"):
    """ Fonction qui affiche avec les bonnes indentations un fichier json

    Args:
        json_data (json): Données json en entrée
        file (str, optional): Nom de fichier json de sortie "sample.json".
        mode (str, optional): Defaults to "a" pour "append" - "w" pour "write"
    """
    # print(json_data)
    json_formatted_str = json.dumps(
        json_data, indent=2, default=palangre_syc.api.serialize)
    with open(file, mode) as outfile:
        outfile.write(json_formatted_str)


DIR = "./palangre_syc/media"




# if __name__ == "__main__":
#     start_time = time.time()
#     main()
#     print("--- %s seconds ---" % (time.time() - start_time))
