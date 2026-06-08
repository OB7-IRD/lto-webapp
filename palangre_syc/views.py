import time

import os
# import re
import json
# import datetime
import warnings

import pandas as pd
import numpy as np

from django.shortcuts import render
from django.contrib import messages
from django.utils.translation import gettext as _

from pathlib import Path
from palangre_syc import excel_extractions
from palangre_syc import json_construction
from api_traitement import api_functions, common_functions
from website.settings import MEDIA_ROOT ,LOGBOOKS_DIR ,DATA_DIR, TEMP_DIR  
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_previous_trip_infos(request, token, df_donnees_p1, allData):
    """Fonction qui va faire appel au WS pour :
    1) trouver l'id du trip le plus récent pour un vessel et un programme donné
    2) trouver les informations rattachées à ce trip
    - Utilise ThreadPoolExecutor pour paralléliser les appels API
    """

    base_url = request.session.get('base_url')

    vessel_topiaid = json_construction.get_vessel_topiaid(df_donnees_p1, allData)
    vessel_topiaid_ws = vessel_topiaid.replace("#", "-")
    programme_topiaid = request.session.get('dico_config')['programme']
    programme_topiaid_ws = programme_topiaid.replace("#", "-")

    print("="*20, vessel_topiaid_ws, "="*20)
    print("="*20, programme_topiaid_ws, "="*20)

    route = '/data/ll/common/Trip'
    previous_trip = api_functions.trip_for_prog_vessel(
        token, base_url, route, vessel_topiaid_ws, programme_topiaid_ws
    )

    parsed_previous_trip = json.loads(previous_trip.decode('utf-8'))

    if not parsed_previous_trip['content']:
        return None

    print(f"Pour ce programme et ce vessel : {len(parsed_previous_trip['content'])} trips enregistrés")

    # ── Fonction appelée en parallèle pour chaque trip ──────────────
    def fetch_trip_details(num_trip):
        """Récupère les détails d'un trip depuis l'API Observe."""
        try:
            trip_topiaid = parsed_previous_trip['content'][num_trip]['topiaId'].replace("#", "-")
            trip_info = json.loads(
                api_functions.get_one_from_ws(
                    token, base_url, '/data/ll/common/Trip/', trip_topiaid
                ).decode('utf-8')
            )
            return num_trip, trip_info
        except Exception as e:
            print(f"Erreur fetch trip {num_trip}: {e}")
            return num_trip, None

    # ── Appels parallèles ────────────────────────────────────────────
    nb_trips = len(parsed_previous_trip['content'])
    trip_results = {}

    with ThreadPoolExecutor(max_workers=min(nb_trips, 5)) as executor:
        futures = {
            executor.submit(fetch_trip_details, i): i
            for i in range(nb_trips)
        }
        for future in as_completed(futures):
            num_trip, trip_info = future.result()
            if trip_info is not None:
                trip_results[num_trip] = trip_info

    # ── Construction du DataFrame dans l'ordre ───────────────────────
    df_trip = pd.DataFrame(
        columns=["triptopiaid", "startDate", "depPort_topiaid", "depPort",
                 "endDate", "endPort_topiaid", "endPort", "ocean"]
    )

    lang = request.LANGUAGE_CODE
    label_key = 'label2' if lang == 'fr' else 'label1'

    for num_trip in sorted(trip_results.keys()):
        trip_info = trip_results[num_trip]
        content = trip_info['content'][0]

        # Port de départ
        if 'departureHarbour' in content:
            depPort = content['departureHarbour']
            depPort_name = common_functions.from_topiaid_to_value(
                topiaid=depPort,
                lookingfor='Harbour',
                label_output=label_key,
                allData=allData,
                domaine=None
            )
        else:
            depPort = None
            depPort_name = None

        # Port d'arrivée
        if 'landingHarbour' in content:
            endPort = content['landingHarbour']
            endPort_name = common_functions.from_topiaid_to_value(
                topiaid=endPort,
                lookingfor='Harbour',
                label_output=label_key,
                allData=allData,
                domaine=None
            )
        else:
            endPort = None
            endPort_name = None

        # Océan
        ocean = common_functions.from_topiaid_to_value(
            topiaid=content['ocean'],
            lookingfor='Ocean',
            label_output=label_key,
            allData=allData,
            domaine=None
        )

        df_trip.loc[num_trip] = [
            content['topiaId'],
            content['startDate'],
            depPort,
            depPort_name,
            content['endDate'],
            endPort,
            endPort_name,
            ocean
        ]

    # ── Nettoyage nan → None pour sérialisation JSON ─────────────────
    df_trip = df_trip.where(df_trip.notna(), other=None)

    return df_trip
    

def presenting_previous_trip(request):
    """Function that get all the trip associated to the vessel and the program selected

    Args:
        request

    Returns:
        html page with a table of the existings trips in observe
    """
    print("#"*25,"\nStart presenting_previous_trip \n", request.session.get('dico_config'), "\n", "#"*25)

    # Vérification que media/data/ contient bien un fichier
    data_files = [f for f in DATA_DIR.iterdir() if f.is_file()]
    if not data_files:
        messages.error(request, _("Les données de référence sont absentes. Veuillez effectuer une mise à jour."))
        return redirect('logbook')
    allData_file_path = str(data_files[0])
    request.session['allData_file_path'] = allData_file_path
    allData = common_functions.load_json_file(allData_file_path)

    if 'context' in request.session:
        del request.session['context']
        
    selected_file = request.GET.get('selected_file')
    apply_conf = request.session.get('dico_config')

    print("="*20, "presenting_previous_trip", "="*20)

    if request.LANGUAGE_CODE == 'fr':
        programme = common_functions.from_topiaid_to_value(topiaid=apply_conf['programme'],
                                        lookingfor='Program',
                                        label_output='label2',
                                        allData=allData,
                                        domaine='palangre')

        ocean = common_functions.from_topiaid_to_value(topiaid=apply_conf['ocean'],
                                    lookingfor='Ocean',
                                    label_output='label2',
                                    allData=allData,
                                    domaine=None)
        
    elif request.LANGUAGE_CODE == 'en':
        programme = common_functions.from_topiaid_to_value(topiaid=apply_conf['programme'],
                                        lookingfor='Program',
                                        label_output='label1',
                                        allData=allData,
                                        domaine='palangre')

        ocean = common_functions.from_topiaid_to_value(topiaid=apply_conf['ocean'],
                                    lookingfor='Ocean',
                                    label_output='label1',
                                    allData=allData,
                                    domaine=None)

    context = dict(domaine=apply_conf['domaine'], program=programme, programtopiaid=apply_conf['programme'],
                    ocean=ocean, oceantopiaid=apply_conf['ocean'], version=apply_conf['ty_doc'])

    logbook_file_path = request.session.get('logbook_file_path')
    if not logbook_file_path or not Path(logbook_file_path).exists():
        messages.error(request, _("Fichier logbook introuvable. Veuillez le déposer à nouveau."))
        return redirect('logbook')

    df_donnees_p1 = common_functions.read_excel(logbook_file_path, 1)

    token = request.session['token']
    base_url = request.session['base_url']
    if not api_functions.is_valid(base_url, token):
        username = request.session.get('username')
        password = request.session.get('password')
        database = request.session.get('database')
        client_app_version = request.session.get('client_app_version')
        model_version = request.session.get('model_version')
        referential_locale = request.session.get('referential_locale')
        token = api_functions.reload_token(
            username=username,
            password=password,
            base_url=base_url,
            database=database,
            client_app_version=client_app_version,
            model_version=model_version,
            referential_locale=referential_locale
        )
        request.session['token'] = token

    try:
        start_time = time.time()
        df_previous_trip = get_previous_trip_infos(request, token, df_donnees_p1, allData)
        end_time = time.time()
        print("Temps d'exécution:", end_time - start_time, "secondes")

        if df_previous_trip is not None:
            df_previous_trip = df_previous_trip.to_dict("index")
            context.update({'df_previous': df_previous_trip})

    except Exception as e:
        print("Erreur get_previous_trip_infos:", e)
        context.update({'df_previous': None})

    request.session['context'] = context
    print("---"*50, "context saved")
    print(context)
    return render(request, 'LL_previoustrippage.html', context)


def checking_logbook(request):
    """
    Fonction qui 
    1) affiche les données extraites du logbook soumis 
    2) vérifie et valide les données saisies par l'utilisateur

    Args:
        request 

    Returns:
        Si les données soumises ne sont pas cohérentes : on retourne la meme page avec un message d'erreur adapté 
        Si non : on envoie le logbook
    """
    
    print("="*20, "checking_logbook", "="*20)
    
    allData_file_path = request.session.get('allData_file_path')
    allData = common_functions.load_json_file(allData_file_path)

    token = request.session['token']
    base_url = request.session['base_url']
    if not api_functions.is_valid(base_url, token):
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
        request.session['token'] = token

    base_url = request.session.get('base_url')
    # base_url = 'https://observe.ob7.ird.fr/observeweb/api/public'

    if request.method == 'POST':
            
        apply_conf = request.session.get('dico_config')
        print("apply_conf : ", apply_conf)
        continuetrip = request.POST.get('continuetrip')
        newtrip = request.POST.get('newtrip')
        context = request.session.get('context')
        print("+"*50, "Juste après le post", "+"*50)
        print(context)
        print("+"*50, "END Juste après le post", "+"*50)
        
        
        #_______________________________EXTRACTION DES DONNEES__________________________________
        logbook_file_path = request.session.get('logbook_file_path')
                
        df_donnees_p1 = common_functions.read_excel(logbook_file_path, 1)
        # df_donnees_p2 = common_functions.read_excel(logbook_file_path, 2)
        
        # Common to both logbooks
        df_vessel = excel_extractions.extract_vessel_info(df_donnees_p1)
        df_cruise = excel_extractions.extract_cruise_info(df_donnees_p1, version = apply_conf['ty_doc'])
        df_report = excel_extractions.extract_report_info(df_donnees_p1, version = apply_conf['ty_doc'])
        df_gear = excel_extractions.extract_gear_info(df_donnees_p1, version = apply_conf['ty_doc'])
        df_target = excel_extractions.extract_target_species(df_donnees_p1, version = apply_conf['ty_doc'])
        df_date = excel_extractions.extract_logbook_date(df_donnees_p1, version = apply_conf['ty_doc'])
        df_fishing_effort = excel_extractions.extract_fishing_effort(df_donnees_p1, version = apply_conf['ty_doc'])
        df_position = excel_extractions.extract_positions(df_donnees_p1, version = apply_conf['ty_doc'])
        df_time = excel_extractions.extract_time(df_donnees_p1, allData, version = apply_conf['ty_doc'])
        df_temperature = excel_extractions.extract_temperature(df_donnees_p1, version = apply_conf['ty_doc'])
        
        if (apply_conf['ty_doc'] == 'll_17.6'):
            df_line = excel_extractions.extract_line_material_v17(df_donnees_p1)
            df_bait = excel_extractions.extract_bait_v17(df_donnees_p1)
            # df_fishes = excel_extractions.extract_fish_p1_v17(df_donnees_p1)
            # df_bycatch = excel_extractions.extract_bycatch_p2_v17(df_donnees_p2)
        elif (apply_conf['ty_doc'] == 'll_26'):
            print("Extraction logbook v26")
            # df_donnees_p3 = common_functions.read_excel(logbook_file_path, 3)
            # df_donnees_p4 = common_functions.read_excel(logbook_file_path, 4)
            
            df_line = excel_extractions.extract_line_material_v26(df_donnees_p1)
            df_bait = excel_extractions.extract_bait_v26(df_donnees_p1)['Bait'].unique()
            # df_fishes = excel_extractions.extract_fish_p1_v26(df_donnees_p1)
            # df_bycatch_sharks = excel_extractions.extract_bycatch_p2_v26(df_donnees_p2)
            # df_bycatch_oth = excel_extractions.extract_bycatch_p3_v26(df_donnees_p3)
            # df_bycatch = pd.concat([df_bycatch_sharks, df_bycatch_oth], axis=1)
            
            # df_ref_material = excel_extractions.extract_material_ref(df_donnees_p4)

        if len(df_time['VesselActivity_topiaId'].unique()) == 1 and df_time['VesselActivity_topiaId'].unique()[0] == "fr.ird.referential.ll.common.VesselActivity#666#04":
            print("outside all month")
            df_position = df_position.iloc[:len(df_position)]
        # on ajuste le dataframe pour que ca s'arrête à la fin du mois
        elif "fr.ird.referential.ll.common.VesselActivity#666#04" in df_time['VesselActivity_topiaId'].unique():
            df_position = df_position.iloc[:len(df_position)]
        else : 
            df_position = common_functions.remove_if_nul(df_position, 'Latitude')
        
        # Si on n'a plus d'activité a la fin de df (mais elles sont id comme "Unknonw")
        if "fr.ird.referential.ll.common.VesselActivity#666#07" in df_time['VesselActivity_topiaId'].unique():
            # Tant que la dernière ligne est Unknown
            while (not df_time.empty and str(df_time.iloc[-1]['VesselActivity_topiaId']) == "fr.ird.referential.ll.common.VesselActivity#666#07"):
                df_time = df_time.iloc[:-1]

        if len(df_position) != len(df_time):
            df_time_month = df_time[0:len(df_position)]
            df_temperature_month = df_temperature[0:len(df_position)]
            df_fishing_effort_month = df_fishing_effort[0:len(df_position)]
            # df_fishes_month = df_fishes[0:len(df_position)]
            # df_bycatch_month = df_bycatch[0:len(df_position)]
            
        else :
            df_time_month = df_time
            df_temperature_month = df_temperature
            df_fishing_effort_month = df_fishing_effort
            # df_fishes_month = df_fishes
            
            # df_bycatch_month = df_bycatch
        
        df_activity = pd.concat([df_fishing_effort_month.loc[:,'Day'], 
                                    df_position, 
                                    df_time_month.loc[:, ['VesselActivity', 'Time']], 
                                    df_temperature_month,
                                    df_fishing_effort_month.loc[:,['Hooks per basket', 'Total hooks', 'Total lightsticks']],
                                    # df_fishes_month,
                                    # df_bycatch_month
                                    ],
                                    axis=1)

        list_ports = common_functions.get_list_harbours(allData)
        
        data_to_homepage = {
            'version': apply_conf['ty_doc'],
            'df_vessel': df_vessel,
            'df_cruise': df_cruise,
            'list_ports': list_ports,
            'df_report': df_report,
            'df_gear': df_gear,
            'df_line': df_line,
            'df_target': df_target,
            'df_date': df_date,
            'df_bait': df_bait,
            'df_position': df_position,
            'df_time': df_time,
            'df_activity': df_activity,}
        #_______________________________EXTRACTION DES DONNEES__________________________________
        
        at_port_checkbox = request.POST.get('atportcheckbox')
        startDate = request.POST.get('startDate')
        depPort = request.POST.get('depPort')
        endDate = request.POST.get('endDate')
        endPort = request.POST.get('endPort')
        
        if newtrip != None : 
            context.update({'df_previous': None})
            
        #############################
        # messages d'erreurs
        if df_time_month['Day'][0] != 1:
            messages.error(request, _("L'extraction des données ne semble pas correcte car ne commence pas au jour 1. Veuillez vérifier que le tableau commence ligne 22 sur votre logbook."))
            probleme = True
        #############################
                
        ######### Si on a rempli les données demandées, on vérifie ce qui a été saisi
        if endDate is not None :
            print("+"*50, "phase de validation", "+"*50)
            print(context)
            print("+"*50, "END phase de validation", "+"*50)
            
            probleme = False
            
            logbook_month = str(df_date.loc[df_date['Logbook_name'] == 'Month', 'Value'].values[0])
            logbook_year = str(df_date.loc[df_date['Logbook_name'] == 'Year', 'Value'].values[0])
            
            context.update({'endDate' : json_construction.create_starttimestamp_from_field_date(endDate),
                            'endPort': endPort if endPort != '' else None})
            
            #############################
            # messages d'erreurs
            if (int(context['endDate'][5:7]) + int(context['endDate'][:4])) != (int(logbook_month) + int(logbook_year)):
                print(int(context['endDate'][5:7]) + int(context['endDate'][:4]), "!= ", int(logbook_month) + int(logbook_year))
                messages.error(request, _("La date de fin de trip doit être dans le mois. Saisir le dernier jour du mois dans le cas où le trip n'est pas réellement fini."))
                probleme = True
            #############################
            
            #############################
            # messages d'erreurs
            if ('VesselActivity' in df_time.columns and
                df_time['VesselActivity_topiaId'].astype(str).ne("fr.ird.referential.ll.common.VesselActivity#666#04").any()):
                if isinstance(df_gear, tuple):
                    messages.error(request, _("Les informations concernant la longueur du matériel de pêche doivent être des entiers."))
                    probleme = True
            #############################
            
            #############################
            # messages d'erreurs
            if ('VesselActivity' in df_time.columns and
                df_time['VesselActivity_topiaId'].astype(str).eq("fr.ird.referential.ll.common.VesselActivity#666#07").any()):
                messages.error(request, _("La valeur 'Unknown' est détectée dans Vessel activity - Vérifier que les 'Fishing activity' sont bien saisies."))
                probleme = True
            #############################
            
            
            # if context['df_previous'] == None or len(context['df_previous']) != 1:
            #     # NOUVELLE MAREE
            #     context.update({'startDate': json_construction.create_starttimestamp_from_field_date(startDate),
            #                     'depPort': depPort,
            #                     'endDate' : json_construction.create_starttimestamp_from_field_date(endDate),
            #                     'endPort': endPort if endPort != '' else None,
            #                     'continuetrip': None})
                
            #     #############################
            #     is_dep_match = research_dep(df_donnees_p1, allData, startDate)
            #     if is_dep_match is False:
            #         messages.warning(request, _("La date de début de marée que vous avez saisie ne semble pas correspondre à une activité 'departure' du logbook. Vérifiez les données."))
            #         probleme = True
            #     #############################
            
            # try:
                
            if context['df_previous'] == None:
                # NOUVELLE MAREE
                context.update({'at_port_checkbox': at_port_checkbox, 
                                'startDate': json_construction.create_starttimestamp_from_field_date(startDate),
                                'depPort': depPort,
                                'endDate' : json_construction.create_starttimestamp_from_field_date(endDate),
                                'endPort': endPort if endPort != '' else None,
                                'continuetrip': None})
                
                #############################
                # is_dep_match = research_dep(df_donnees_p1, allData, startDate)
                # print(is_dep_match)
                # if is_dep_match is False:
                #     messages.warning(request, _("La date de début de marée que vous avez saisie ne semble pas correspondre à une activité 'departure' du logbook. Vérifiez les données."))
                #     probleme = True
                #############################
            
            else:
                # CONTINUE TRIP
                # context.update({'df_previous' : pd.DataFrame.from_dict(context['df_previous'], orient = 'index')})
                # context.update({'df_previous' : context['df_previous'], orient = 'index')})
                
                with open(TEMP_DIR / 'previous_trip.json', 'r', encoding='utf-8') as f:
                    json_previoustrip = json.load(f)
                
                # On récupère la date du jour 1 au bon format
                if df_time.loc[0, 'VesselActivity'] == "fr.ird.referential.ll.common.VesselActivity#1239832686138#0.1":
                    # Si c'est une fishing operation
                    date = json_construction.create_starttimestamp(df_donnees_p1, allData, version = apply_conf['ty_doc'], index_day = 0, need_hour = True)
                else:
                    date = json_construction.create_starttimestamp(df_donnees_p1, allData, version = apply_conf['ty_doc'], index_day = 0, need_hour = False)

                #############################
                # messages d'erreurs
                prev_month = int(context['df_previous']['endDate'][5:7])
                prev_year = int(context['df_previous']['endDate'][:4])
                curr_month =  int(logbook_month) 
                curr_year = int(logbook_year)
                
                if json_construction.search_date_into_json(json_previoustrip['content'], date) is True:
                    messages.warning(request, _("Le logbook soumis n'a pas pu être saisi dans la base de données car il a déjà été envoyé dans un précédent trip. Merci de vérifier sur l'application"))
                    probleme = True                
                
                elif prev_month == 12 and curr_month == 1 and curr_year != prev_year + 1:

                    probleme = True
                    messages.warning(request, _("Le logbook soumis n'a pas pu être saisi dans la base de données car il n'est pas consécutif à la marée précédente"))
                    
                elif prev_month != 12 and curr_month != 1 and curr_year != prev_year and curr_month != prev_month + 1:
                    probleme = True
                    messages.warning(request, _("Le logbook soumis n'a pas pu être saisi dans la base de données car il n'est pas consécutif à la marée précédente"))
                                    
                context.update({'at_port_checkbox': at_port_checkbox, 
                                'startDate': context['df_previous']['startDate'], 
                                'depPort': context['df_previous']['depPort_topiaid'],
                                'endDate' : json_construction.create_starttimestamp_from_field_date(endDate),
                                'endPort': endPort if endPort != '' else None, 
                                'continuetrip': 'Continuer cette marée'})
                print("- 0 -"*30)
                print(context)
                print("- 0 -"*30)
                # voir si faut ajouter un truc qui ré enregistre à la session ? 

            if probleme is True:
                # on doit ajouter les infos quand meme 
                data_to_homepage.update({'programme': context['program'],
                                        'ocean': context['ocean'],})
                
                if context['df_previous'] is not None : 
                    data_to_homepage.update({'previous_trip': context['df_previous'],
                            'continuetrip': context['continuetrip'],})
                
                return render(request, 'LL_presenting_logbook.html', data_to_homepage)
            
            else :
                return send_logbook2observe(request)
                
            
        # print("continue the trip : ", continuetrip)
        
        if request.LANGUAGE_CODE == 'fr':
            programme = common_functions.from_topiaid_to_value(topiaid=apply_conf['programme'],
                                        lookingfor='Program',
                                        label_output='label2',
                                        allData=allData,
                                        domaine='palangre')
            
            ocean = common_functions.from_topiaid_to_value(topiaid=apply_conf['ocean'],
                                        lookingfor='Ocean',
                                        label_output='label2',
                                        allData=allData,
                                        domaine=None)
            
        elif request.LANGUAGE_CODE == 'en':
            programme = common_functions.from_topiaid_to_value(topiaid=apply_conf['programme'],
                                        lookingfor='Program',
                                        label_output='label1',
                                        allData=allData,
                                        domaine='palangre')
            
            ocean = common_functions.from_topiaid_to_value(topiaid=apply_conf['ocean'],
                                lookingfor='Ocean',
                                label_output='label1',
                                allData=allData,
                                domaine=None)

        context = {'domaine': apply_conf['domaine'],
                    'program': programme,
                    'programtopiaid' : apply_conf['programme'],
                    'ocean': ocean, 
                    'oceantopiaid': apply_conf['ocean'], 
                    'version' : apply_conf['ty_doc']}
        
            
        # si on contiue un trip, on récupère ses infos pour les afficher
        # if continuetrip is not None and request.POST.get('radio_previoustrip') is not None: 
        if continuetrip is not None and 'radio_previoustrip' in request.POST:
            # si on a choisi de continuer un trip 
            triptopiaid = request.POST.get('radio_previoustrip')      
            trip_topiaid_ws = triptopiaid.replace("#", "-")
            print("="*20, trip_topiaid_ws, "="*20)
            
            # on récupère les infos du trip enregistré dans un fichier json
            route = '/data/ll/common/Trip/'
            previous_trip_info = api_functions.get_one_from_ws(token, base_url, route, trip_topiaid_ws)
            json_previoustrip = json.loads(previous_trip_info)
            
            # on enregistre dans le dossier les informations relatives au précédent trip qu'on veut continuer
            previous_trip_path = TEMP_DIR / 'previous_trip.json'
            if previous_trip_path.exists():
                previous_trip_path.unlink()
            TEMP_DIR.mkdir(parents=True, exist_ok=True)
            with open(previous_trip_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(json_previoustrip, ensure_ascii=False, indent=4))
            
            json_previoustrip = json_previoustrip["content"][0]
            # On récupère les infos qu'on veut afficher (test si le captain est saisi)
            if ('captain' in dict.keys(json_previoustrip)) :
                captain_name = common_functions.from_topiaid_to_value(topiaid=json_previoustrip['captain'],
                                                lookingfor='Person',
                                                label_output='lastName',
                                                allData=allData,
                                                domaine=None)
            else :
                captain_name = None

            vessel_name = common_functions.from_topiaid_to_value(topiaid=json_previoustrip['vessel'],
                                                lookingfor='Vessel',
                                                label_output='label2',
                                                allData=allData,
                                                domaine=None)
            dico_trip_infos = {'startDate': json_previoustrip['startDate'],
                                'endDate': json_previoustrip['endDate'],
                                'captain': captain_name,
                                'vessel': vessel_name,
                                'triptopiaid': triptopiaid}

            try:
                departure_harbour = common_functions.from_topiaid_to_value(topiaid=json_previoustrip['departureHarbour'],
                                                        lookingfor='Harbour',
                                                        label_output='label2',
                                                        allData=allData,
                                                        domaine=None)

                dico_trip_infos.update({
                    'depPort': departure_harbour,
                    'depPort_topiaid': json_previoustrip['departureHarbour'],
                })

            except KeyError:
            # en théorie devrait plus y avoir ce soucis car le departure harbour sera mis en champ obligatoire 
                dico_trip_infos.update({
                    'depPort': 'null',
                    'depPort_topiaid': 'null',
                })
                        
        else : 
            dico_trip_infos = None
            continuetrip = None
            print("on est dans le else et continue the trip = ", continuetrip)
        
        context.update({"df_previous" : dico_trip_infos,
                        "continuetrip": continuetrip})

        print("+"*50, "A la fin de la fonction", "+"*50)
        print(context)
        print("+"*50, "END A la fin de la fonction", "+"*50)
        request.session['context'] = context

        data_to_homepage.update({
            'programme': context['program'],
            'ocean': context['ocean'],
            'previous_trip': dico_trip_infos,
            'continuetrip': continuetrip,
        })
        return render(request, 'LL_presenting_logbook.html', data_to_homepage)

    else:
        # Gérer le cas où la méthode HTTP n'est pas POST
        pass
    return render(request, 'LL_presenting_logbook.html')


def send_logbook2observe(request):
    """
    Fonction qui envoie
    1) le trip si on créé un nouveau trip 
    2) supprime et envoie le nouveau trip updated si on ajoute des informations de marée à un trip existant
    """

    allData_file_path = request.session.get('allData_file_path')
    allData = common_functions.load_json_file(allData_file_path)
    # allData = common_functions.load_allData_file()
    
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if request.method == 'POST':
        print("°"*20, "POST", "°"*20)

        logbook_file_path = request.session.get('logbook_file_path')
        context = request.session.get('context')
        resultat = None
        

        created_json_path = TEMP_DIR / 'created_json_file.json'
        if created_json_path.exists():
            created_json_path.unlink()

        print("="*80)
        print("Load JSON data file")

        token = request.session['token']
        base_url = request.session['base_url']
        if not api_functions.is_valid(base_url, token):
            username = request.session.get('username')
            password = request.session.get('password')
            database = request.session.get('database')
            client_app_version = request.session.get('client_app_version')  # Peut être None
            model_version = request.session.get('model_version')            # Peut être None
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
            request.session['token'] = token
            
        base_url = request.session.get('base_url')
        
        print("="*80)
        print("Read excel file")
        print(logbook_file_path)
        
        df_donnees_p1 = common_functions.read_excel(logbook_file_path, 1)
        df_donnees_p2 = common_functions.read_excel(logbook_file_path, 2)
        
        if context['version'] == 'll_26':
            df_donnees_p3 = common_functions.read_excel(logbook_file_path, 3)
            df_donnees_p4 = common_functions.read_excel(logbook_file_path, 4)
    
        # On transforme pour que les données soient comparables
        logbook_month = str(excel_extractions.extract_logbook_date(df_donnees_p1, version=context['version']).loc[excel_extractions.extract_logbook_date(df_donnees_p1, version=context['version'])['Logbook_name'] == 'Month', 'Value'].values[0])

        if len(logbook_month) == 1:
            logbook_month = '0' + logbook_month
            print(logbook_month, type(logbook_month))
        else:
            logbook_month = str(logbook_month)
        
        startDate = context['startDate'] 
        
        if startDate[5:7] == logbook_month:
            start_extraction = int(startDate[8:10]) - 1
            if context['endDate'][5:7] == logbook_month:
                end_extraction = int(context['endDate'][8:10])
            else:
                end_extraction = len(excel_extractions.extract_positions(df_donnees_p1, version=context['version']))
        else:
            start_extraction = 0
            end_extraction = int(context['endDate'][8:10])
            
        if context['continuetrip'] is None:
            # NEW TRIP
            
            print("="*80)
            print("Create Activity and Set")

            if context['version'] == 'll_17.6':
                MultipleActivity = json_construction.create_activity_and_set(
                    start_extraction, end_extraction, context, 
                    allData,
                    df_donnees_p1, df_donnees_p2,
                    df_donnees_p3=None, df_donnees_p4=None)
                
            elif context['version'] == 'll_26':
                MultipleActivity = json_construction.create_activity_and_set(
                    start_extraction, end_extraction, context, 
                    allData,
                    df_donnees_p1, df_donnees_p2,
                    df_donnees_p3=df_donnees_p3, 
                    df_donnees_p4=df_donnees_p4)

            print("="*80)
            print("Create Trip")
            
            trip = json_construction.create_trip(df_donnees_p1, MultipleActivity, allData, context)

            print("Creation of a new trip")
            route = '/data/ll/common/Trip'
            print("base url ::: ", base_url)
            print("token ::: ", token)
            resultat, code = api_functions.send_trip(token, trip, base_url, route)
            
            # if len(resultat[0]) > 1:
            #     resultat = resultat[0][0]
            
            print("resultats : ", resultat)
            
        else:   
            # CONTINUE THE TRIP 
            
            with open(TEMP_DIR / 'previous_trip.json', 'r', encoding='utf-8') as f:
                json_previoustrip = json.load(f)
            
            if context['version'] == 'll_17.6':
                MultipleActivity = json_construction.create_activity_and_set(
                    start_extraction, end_extraction, context, 
                    allData,
                    df_donnees_p1, df_donnees_p2,
                    df_donnees_p3=None, df_donnees_p4=None)
                
            elif context['version'] == 'll_26':
                MultipleActivity = json_construction.create_activity_and_set(
                    start_extraction, end_extraction, context, 
                    allData,
                    df_donnees_p1, df_donnees_p2,
                    df_donnees_p3=df_donnees_p3, 
                    df_donnees_p4=df_donnees_p4)

            print("="*80)
            print("Update Trip")

            trip = json_previoustrip['content']
            # On ajoute les acitivités du nouveau logbook
            for day in range(len(MultipleActivity)):
                trip[0]['activityLogbook'].append(MultipleActivity[day])
            
            
            trip[0]["endDate"] = context['endDate']
            if context['endPort'] is not None : 
                trip[0]["landingHarbour"] = context['endPort']

            # on homogénéise les données extraites de la base, et les nouvelles données qu'on implémente :
            trip = json_construction.replace_null_false_true(trip)
            trip = json_construction.remove_keys(trip, ["topiaId", "topiaCreateDate", "lastUpdateDate"])[0]
                                
            # permet de visualiser le fichier qu'on envoie
            # json_formatted_str = json.dumps(json_construction.remove_keys(trip, ["topiaId", "topiaCreateDate", "lastUpdateDate"]),
            #                                 indent=2,
            #                                 default=api.serialize)
        
            # with open(file="media/temporary_files/updated_json_file.json", mode="w") as outfile:
            #     outfile.write(json_formatted_str)

            resultat, code = api_functions.update_trip(token=token,
                            data=trip,
                            base_url=base_url,
                            topiaid=context['df_previous']['triptopiaid'].replace("#", "-"))
    
            # print("Creation of a new trip")
            # route = '/data/ll/common/Trip'
            # print("base url ::: ", base_url)
            # print("token ::: ", token)
            # resultat, code = api_functions.send_trip(token, trip, base_url, route)
            
        
        if code == 1:
            messages.success(request, _("Le logbook a bien été envoyé dans la base"))
        
        elif code == 2: 
            # messages.error(request, _("Il doit y avoir une erreur dedans car le logbook n'a pas été envoyé"))
            for error_message in resultat:
                messages.error(request, error_message)
        
        else : 
            messages.warning(request, resultat)

        return render(request, 'LL_send_data.html')

    else:
        # ajouter une page erreur d'envoi
        return render(request, 'LL_file_selection.html')
