"""
#######################################################
#
# Fonctions relatives à la constitution du json pour la seine 
# selon le logbook version 23
#
#######################################################
"""

def js_content(tab6_routeLogbook, oce = None, program = None):
    return {
      "homeId": None, # Premiere page marée sous le nom du patron si donnée mettre  sinon None ou None #OK
      "startDate": None,
      "endDate": None,
      "historicalData": False,
      "ocean": oce,
      "generalComment": "Marée insérée depuis le service web",
      "observationsComment": None,

      "routeLogbook": tab6_routeLogbook,

      "vessel": None,

      "logbookProgram": program, # liste generer demander seine dns gearType & logbook = Ture
      "observationsProgram" : None, # Old
      # "observationProgram" : None, # 9.5

      "observer": None,

      "captain": None,  # Nom et prenom person == capitain=True /// Table Person nom prenm & captain
      "logbookDataEntryOperator": None , # inconnu - inconnu flag==saisisseur nom prenm & dataEntryOperato

      "observationsDataEntryOperator": None,

      "departureHarbour": "fr.ird.referential.common.Harbour#11#0.1",
      "landingHarbour": "fr.ird.referential.common.Harbour#11#0.1",

      "logbookDataQuality": "fr.ird.referential.common.DataQuality#0#5",
      "departureWellContentStatus": "fr.ird.referential.ps.logbook.WellContentStatus#1464000000000#03",
      "landingWellContentStatus": "fr.ird.referential.ps.logbook.WellContentStatus#1464000000000#03",
        # observationAcquisitionStatus => Obs 9.5
      # "observationAcquisitionStatus": "fr.ird.referential.ps.common.AcquisitionStatus#1464000000000#099",
       # observationsAcquisitionStatus => Obs old version
      "observationsAcquisitionStatus": "fr.ird.referential.ps.common.AcquisitionStatus#1464000000000#099",
      "logbookAcquisitionStatus": "fr.ird.referential.ps.common.AcquisitionStatus#1464000000000#001",
      "targetWellsSamplingAcquisitionStatus": "fr.ird.referential.ps.common.AcquisitionStatus#1464000000000#999",
      "landingAcquisitionStatus": "fr.ird.referential.ps.common.AcquisitionStatus#1464000000000#999",
      "localMarketAcquisitionStatus": "fr.ird.referential.ps.common.AcquisitionStatus#1464000000000#999",
      "localMarketWellsSamplingAcquisitionStatus": "fr.ird.referential.ps.common.AcquisitionStatus#1464000000000#999",
      "localMarketSurveySamplingAcquisitionStatus": "fr.ird.referential.ps.common.AcquisitionStatus#1464000000000#999",
      "advancedSamplingAcquisitionStatus": "fr.ird.referential.ps.common.AcquisitionStatus#1464000000000#999",
      "activitiesAcquisitionMode":None # [BY_NUMBER, BY_TIME]
}


def js_Float():
    return {
    "whenArriving": False,
    "whenLeaving": False,
    "objectMaterial": None,
  }

def js_Transmitt():
    return {

    "transmittingBuoyOwnership": None, #quand on n'a pas d'info on mettre le top Id a un bateau inconu
    "transmittingBuoyType": None, #chercher l'ID avec le m3i
    "transmittingBuoyOperation": None, #chercher aussi = deja present(recuperation) ou deployer(mise a l'eau)

  }

def js_floatingObject(tab2_Transmitt, tab1_Float):
    return {
    "comment": None,
    "objectOperation": None,
    "supportVesselName": None,

    "transmittingBuoy": tab2_Transmitt,

    "floatingObjectPart": tab1_Float,

    "computedWhenArrivingBiodegradable": None,
    "computedWhenArrivingNonEntangling": None,
    "computedWhenArrivingSimplifiedObjectType": None,
    "computedWhenLeavingBiodegradable": None,
    "computedWhenLeavingNonEntangling": None,
    "computedWhenLeavingSimplifiedObjectType": None
  }

def js_catche():
    return {

  "comment": None,
  "species": None,
  "weightCategory": None, # Table Ps common #Plus tard
  "speciesFate": None,
  "weight": None,
  "weightMeasureMethod": None
}

def js_activity(tab4_catches, tab3_floatingObject = [], sommeThon = None):
    return {
    "time": None, #"1970-01-01T07:30:00.000Z", #même format heure de peche
    "latitude": None,
    "longitude": None,
    "latitudeOriginal": None, #true
    "longitudeOriginal": None, #true
    "originalDataModified": False,
    "vmsDivergent": False,
    "positionCorrected": False,
    "number": None , #incrementé
    "setCount": None , #si activité de pêche 1 sinon 0 en fonction de vesselActivity
    "setSuccessStatus": None, #######
    "seaSurfaceTemperature": None,
    "windDirection": None,
    "vesselActivity": None, #cherché log partie calé catch + objet = peche code 6 ,objet uniq = code 13 et code 0 pour la premiere et derniere ligne et code 99 par defaut si on a rien
    "totalWeight": sommeThon, #somme des thonage des captures
    "catches": tab4_catches,
    "floatingObject": tab3_floatingObject,
    "observedSystem": [  ############  Correction
                "fr.ird.referential.ps.common.ObservedSystem#1239832686426#0.6606964000652922",
    ],
    "previousFpaZone":None, # Faire un verification de la zone pour voir s'il y a changement de zone
    "nextFpaZone":None # regardant une si la zone change et que les heures et le date sont les mêmes. code 21 vesselActivity
  }


def js_activity2(tab4_catches, tab3_floatingObject = [], sommeThon = None):
    return {
    "time": None, #"1970-01-01T07:30:00.000Z", #même format heure de peche
    "latitude": None,
    "longitude": None,
    "latitudeOriginal": None, #true
    "longitudeOriginal": None, #true
    "originalDataModified": False,
    "vmsDivergent": False,
    "positionCorrected": False,
    "number": None , #incrementé
    "setCount": None , #si activité de pêche 1 sinon 0 en fonction de vesselActivity
    "setSuccessStatus":"fr.ird.referential.ps.logbook.SetSuccessStatus#1464000000000#02", #######
    "seaSurfaceTemperature": None,
    "windDirection": None,
    "vesselActivity": "fr.ird.referential.ps.common.VesselActivity#1239832675368#0.976590514005213", #cherché log partie calé catch + objet = peche code 6 ,objet uniq = code 13 et code 0 pour la premiere et derniere ligne et code 99 par defaut si on a rien
    "totalWeight": sommeThon, #somme des thonage des captures
    "catches": tab4_catches,
    "floatingObject": tab3_floatingObject,
    "observedSystem": [  ############  Correction
                "fr.ird.referential.ps.common.ObservedSystem#1239832686426#0.6606964000652922",
    ]
  }


def js_routeLogbook(tab5_activity):
    return {
    "date": None, #jour de peche
    "activity": tab5_activity
  }