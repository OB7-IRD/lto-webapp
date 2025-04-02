import time

import os
# import re
import json
# import datetime
import warnings


import pandas as pd
import numpy as np
# import openpyxl

from django.shortcuts import render
from django.contrib import messages
from django.utils.translation import gettext as _
# from django.utils import translation
# from django.http import HttpResponseRedirect, JsonResponse
# from django.utils.translation import activate
# from django.template import RequestContext
# from django.urls import reverse
# from django.utils.translation import gettext

from palangre_syc import excel_extractions
from palangre_syc import json_construction
from api_traitement import api_functions, common_functions
# from webapps.models import User

DIR = "./media/logbooks"


# def research_dep(df_donnees_p1, allData, startDate):
#     """
#     Fonction qui recherche si 'dep' est présent dans la case à la date donnée par l'utilisateur

#     Args:
#         df_donnees_p1 (dataframe): _description_
#         allData (dataframe): données de références
#         startDate (date): saisie par l'utilisateur quand on créé une marée

#     Returns:
#         bool: True si la date saisie correspond à un departure, False si non
#     """
#     data = excel_extractions.extract_time(df_donnees=df_donnees_p1, allData=allData)
#     # print("#"*20, "research_dep function", "#"*20)
#     day = startDate[8:10] 
#     dep_rows = data[data['Time'].str.lower().str.contains('dep', case=False, na=False)]
    
#     if not dep_rows.empty:
#         dep_dates = dep_rows['Day']
#         return str(dep_dates.values[0]) in str(day)
#     else:
#         return False


def get_previous_trip_infos(request, token, df_donnees_p1, allData):
    """Fonction qui va faire appel au WS pour :
    1) trouver l'id du trip le plus récent pour un vessel et un programme donné
    et 2) trouver les informations rattachées à ce trip

    Args:
        request (_type_): _description_
        df_donnees_p1 (_type_): _description_

    Returns:
        dictionnaire: startDate, endDate, captain
    """
    
    base_url = request.session.get('base_url')
   
    # les topiaid envoyés au WS doivent être avec des '-' à la place des '#'
    vessel_topiaid = json_construction.get_vessel_topiaid(df_donnees_p1, allData)
    # Pour le webservice, il faut remplacer les # par des - dans les topiaid
    vessel_topiaid_ws = vessel_topiaid.replace("#", "-")
    programme_topiaid = request.session.get('dico_config')['programme']
    programme_topiaid_ws = programme_topiaid.replace("#", "-")

    print("="*20, vessel_topiaid_ws, "="*20)
    print("="*20, programme_topiaid_ws, "="*20)
    route = '/data/ll/common/Trip'
    previous_trip = api_functions.trip_for_prog_vessel(token, base_url, route, vessel_topiaid_ws, programme_topiaid_ws)

    # on récupères les informations uniquement pour le trip avec la endDate la plus récente
    parsed_previous_trip = json.loads(previous_trip.decode('utf-8'))
    if parsed_previous_trip['content'] != []:
        # Prévoir le cas ou le vessel n'a pas fait de trip avant
        print("pour ce programme et ce vessel on a : ", len(parsed_previous_trip['content']), "trip enregistrés")
        
        df_trip = pd.DataFrame(columns=["triptopiaid", "startDate", "depPort_topiaid", "depPort", "endDate", "endPort_topiaid", "endPort", "ocean"])


        for num_trip in range(len(parsed_previous_trip['content'])):
            trip_topiaid = parsed_previous_trip['content'][num_trip]['topiaId'].replace("#", "-")
            route = '/data/ll/common/Trip/'
            # trip_info = json.loads(api.get_trip(token, base_url, trip_topiaid).decode('utf-8'))
            trip_info = json.loads(api_functions.get_one_from_ws(token, base_url, route, trip_topiaid).decode('utf-8'))
            # parsed_trip_info = json.loads(trip_info.decode('utf-8'))
            if 'departureHarbour' in trip_info['content'][0]:
                depPort = trip_info['content'][0]['departureHarbour']
                
                if request.LANGUAGE_CODE == 'fr':
                    depPort_name = common_functions.from_topiaid_to_value(topiaid=depPort,
                                lookingfor='Harbour',
                                label_output='label2',
                                allData=allData,
                                domaine=None)
                elif request.LANGUAGE_CODE == 'en':
                    depPort_name = common_functions.from_topiaid_to_value(topiaid=depPort,
                                lookingfor='Harbour',
                                label_output='label1',
                                allData=allData,
                                domaine=None)
            else : 
                depPort = None
                depPort_name = None
            
            if 'landingHarbour' in trip_info['content'][0]:
                endPort = trip_info['content'][0]['landingHarbour']
                if request.LANGUAGE_CODE == 'fr':
                    endPort_name = common_functions.from_topiaid_to_value(topiaid=endPort,
                                lookingfor='Harbour',
                                label_output='label2',
                                allData=allData,
                                domaine=None)
                elif request.LANGUAGE_CODE == 'en':
                    endPort_name = common_functions.from_topiaid_to_value(topiaid=endPort,
                                lookingfor='Harbour',
                                label_output='label1',
                                allData=allData,
                                domaine=None)
                    
            else : 
                endPort = None
                endPort_name = None
            
            if request.LANGUAGE_CODE == 'fr':
                ocean = common_functions.from_topiaid_to_value(topiaid=trip_info['content'][0]['ocean'],
                                lookingfor='Ocean',
                                label_output='label2',
                                allData=allData,
                                domaine=None)
            elif request.LANGUAGE_CODE == 'en':
                ocean = common_functions.from_topiaid_to_value(topiaid=trip_info['content'][0]['ocean'],
                                lookingfor='Ocean',
                                label_output='label1',
                                allData=allData,
                                domaine=None)
        
            trip_info_row = [trip_info['content'][0]['topiaId'],
                            trip_info['content'][0]['startDate'],
                            depPort,
                            depPort_name,
                            trip_info['content'][0]['endDate'],
                            endPort,
                            endPort_name,
                            ocean] # type: ignore
            
            df_trip.loc[num_trip] = trip_info_row
            
        return(df_trip)
    
    else:
        return None
    

def presenting_previous_trip(request):
    """Function that get all the trip associated to the vessel and the program selected

    Args:
        request

    Returns:
        html page with a table of the existings trips in observe
    """
    # est ce qu'on ne peut pas la mettre en variable globale ?
    # allData = common_functions.load_allData_file()
    allData_file_path = "media/data/" + os.listdir("media/data")[0]
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
                   ocean=ocean, oceantopiaid=apply_conf['ocean'])

    if selected_file is not None and apply_conf is not None:

        file_name = selected_file.strip("['']")
        logbook_file_path = DIR + "/" + file_name

        request.session['logbook_file_path'] = logbook_file_path

        print("="*20, "presenting_previous_trip selected_file", "="*20)
        print(logbook_file_path)

        df_donnees_p1 = common_functions.read_excel(logbook_file_path, 1)

        # on test le token, s'il est non valide, on le met à jour
        token = request.session['token']
        base_url = request.session['base_url']
        if not api_functions.is_valid(base_url, token):
            username = request.session.get('username')
            password = request.session.get('password')
            database = request.session.get('database')
            token = api_functions.reload_token(username, password, base_url, database)
            request.session['token'] = token

        try :
            start_time = time.time()
            df_previous_trip = get_previous_trip_infos(request, token, df_donnees_p1, allData)
            end_time = time.time()
                
            print("Temps d'exécution:", end_time - start_time, "secondes")
            print("°"*20, "presenting_previous_trip - context updated", "°"*20)
            
            if df_previous_trip is not None:
                # Conversion car ne veut pas passer un dataframe en context
                df_previous_trip = df_previous_trip.to_dict("index")
                context.update({'df_previous': df_previous_trip,})
                
                
                        
        except :
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
    
    # allData = api_functions.load_allData_file()
    # file_path = "media/data/" + os.listdir("media/data")[0]
    allData_file_path = request.session.get('allData_file_path')
    allData = common_functions.load_json_file(allData_file_path)

    token = request.session['token']
    base_url = request.session['base_url']
    if not api_functions.is_valid(base_url, token):
        username = request.session.get('username')
        password = request.session.get('password')
        database = request.session.get('database')
        token  = api_functions.reload_token(username, password, base_url, database)
        request.session['token'] = token

    base_url = request.session.get('base_url')
    # base_url = 'https://observe.ob7.ird.fr/observeweb/api/public'

    if request.method == 'POST':
            
        apply_conf = request.session.get('dico_config')
        # print("apply_conf : ", apply_conf)
        continuetrip = request.POST.get('continuetrip')
        newtrip = request.POST.get('newtrip')
        context = request.session.get('context')
        print("+"*50, "Juste après le post", "+"*50)
        print(context)
        print("+"*50, "END Juste après le post", "+"*50)
        
        
        #_______________________________EXTRACTION DES DONNEES__________________________________
        logbook_file_path = request.session.get('logbook_file_path')
                
        df_donnees_p1 = common_functions.read_excel(logbook_file_path, 1)
        df_donnees_p2 = common_functions.read_excel(logbook_file_path, 2)
        
        df_vessel = excel_extractions.extract_vessel_info(df_donnees_p1)
        df_cruise = excel_extractions.extract_cruise_info(df_donnees_p1)
        df_report = excel_extractions.extract_report_info(df_donnees_p1)
        df_gear = excel_extractions.extract_gear_info(df_donnees_p1)
        df_line = excel_extractions.extract_line_material(df_donnees_p1)
        df_target = excel_extractions.extract_target_species(df_donnees_p1)
        df_date = excel_extractions.extract_logbook_date(df_donnees_p1)
        df_bait = excel_extractions.extract_bait(df_donnees_p1)
        df_fishing_effort = excel_extractions.extract_fishing_effort(df_donnees_p1)
        
        df_position = excel_extractions.extract_positions(df_donnees_p1)
        df_time = excel_extractions.extract_time(df_donnees_p1, allData)
        df_temperature = excel_extractions.extract_temperature(df_donnees_p1)
        df_fishes = excel_extractions.extract_fish_p1(df_donnees_p1)
        df_bycatch = excel_extractions.extract_bycatch_p2(df_donnees_p2)

        # on ajuste le dataframe pour que ca s'arrête à la fin du mois
        df_position = common_functions.remove_if_nul(df_position, 'Latitude')

        if len(df_position) != len(df_time):
            df_time_month = df_time[0:len(df_position)]
            df_temperature_month = df_temperature[0:len(df_position)]
            df_fishing_effort_month = df_fishing_effort[0:len(df_position)]
            df_fishes_month = df_fishes[0:len(df_position)]
            df_bycatch_month = df_bycatch[0:len(df_position)]
            
        else :
            df_time_month = df_time
            df_temperature_month = df_temperature
            df_fishing_effort_month = df_fishing_effort
            df_fishes_month = df_fishes
            df_bycatch_month = df_bycatch
        
        df_activity = pd.concat([df_fishing_effort_month.loc[:,'Day'], df_position, df_time_month.loc[:, 'Time'], 
                                    df_temperature_month,
                                    df_fishing_effort_month.loc[:,['Hooks per basket', 'Total hooks', 'Total lightsticks']],
                                    df_fishes_month,
                                    df_bycatch_month],
                                    axis=1)

        list_ports = common_functions.get_list_harbours(allData)
        
        data_to_homepage = {
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
            if isinstance(df_gear, tuple):
                messages.error(request, _("Les informations concernant la longueur du matériel de pêche doivent être des entiers."))
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
                
                with open ('media/temporary_files/previous_trip.json', 'r', encoding='utf-8') as f:
                    json_previoustrip = json.load(f)
                
                # On récupère la date du jour 1 au bon format
                if df_time.loc[0, 'VesselActivity'] == "fr.ird.referential.ll.common.VesselActivity#1239832686138#0.1":
                    # Si c'est une fishing operation
                    date = json_construction.create_starttimestamp(df_donnees_p1, allData, 0, True)
                else:
                    date = json_construction.create_starttimestamp(df_donnees_p1, allData, 0, False)


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
                    print("ce qui permet de garder les infos :"*5)
                    # print(data_to_homepage)
                
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
                    'oceantopiaid': apply_conf['ocean']}
        
            
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
            if os.path.exists("media/temporary_files/previous_trip.json"):
                os.remove("media/temporary_files/previous_trip.json")

            file_name = "media/temporary_files/previous_trip.json"
            with open(file_name, 'w', encoding='utf-8') as f:
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
    # allData_file_path = "media/data/" + os.listdir("media/data")[0]
    allData_file_path = request.session.get('allData_file_path')
    allData = common_functions.load_json_file(allData_file_path)
    # allData = common_functions.load_allData_file()
    
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if request.method == 'POST':
        print("°"*20, "POST", "°"*20)

        logbook_file_path = request.session.get('logbook_file_path')
        context = request.session.get('context')
        resultat = None
        

        if os.path.exists("media/temporary_files/created_json_file.json"):
            os.remove("media/temporary_files/created_json_file.json")

        print("="*80)
        print("Load JSON data file")

        token = request.session['token']
        base_url = request.session['base_url']
        if not api_functions.is_valid(base_url, token):
            username = request.session.get('username')
            password = request.session.get('password')
            database = request.session.get('database')
            token  = api_functions.reload_token(username, password, base_url, database)
            request.session['token'] = token
            
        base_url = request.session.get('base_url')

        print("="*80)
        print("Read excel file")
        print(logbook_file_path)

        df_donnees_p1 = common_functions.read_excel(logbook_file_path, 1)
        df_donnees_p2 = common_functions.read_excel(logbook_file_path, 2)

        # On transforme pour que les données soient comparables
        logbook_month = str(excel_extractions.extract_logbook_date(df_donnees_p1).loc[excel_extractions.extract_logbook_date(df_donnees_p1)['Logbook_name'] == 'Month', 'Value'].values[0])

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
                end_extraction = len(excel_extractions.extract_positions(df_donnees_p1))
        else:
            start_extraction = 0
            end_extraction = int(context['endDate'][8:10])
            
        if context['continuetrip'] is None:
            # NEW TRIP
            
            print("="*80)
            print("Create Activity and Set")

            MultipleActivity = json_construction.create_activity_and_set(
                df_donnees_p1, df_donnees_p2,
                allData,
                start_extraction, end_extraction, context)

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
            
            with open ('media/temporary_files/previous_trip.json', 'r', encoding='utf-8') as f:
                json_previoustrip = json.load(f)

            MultipleActivity = json_construction.create_activity_and_set(
                df_donnees_p1, df_donnees_p2, 
                allData, 
                start_extraction, end_extraction, context)

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
