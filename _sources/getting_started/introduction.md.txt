Welcome to Application d'import des données LogBook's documentation!
====================================================================

Global introduction
===================

To briefly introduce the Django webapp : 
The aim is to automatically send different sourced files to the [Observe](https://umr-marbec.fr/en/the-observatories/ob7) database (add a better link there). 
The sourcing files can be logbooks, observations files or ERS data. 

For now, the app is developed for the purseiners' logbooks and in development for the purseiners' observations files (or ERS - not sure what Adelphe is doing) and longliners' logbooks. 

The input data varies depending on the type of fishering we are studying (purseiners - ps/longliners - ll). The webapp project is then sliced into the ps and the ll. 


Webapp navigation
=================

To access the webapp, a connection trough the Observe database id is mandatory. 

Afterwards, depending on the data you have and want to send to the database, you get to choose : 

* the ocean,
* the type of fishering,
* the program you want the data to go in, 
* the type of input data you have (logbooks, observation, ERS)

You then get to the drop zone platfrom. Selecting all the previous info helps the webapp to treat the specific input data you are submitting. You can then send them to the Observe api. If there is some types errors in the cells or some unexpected operating informations, you will be notified.


Project layout
==============

Here we present the hierarchical structure of the webapp

(Still in construction)

    OBSERVE-LOGBOOKS-READER-WEBAPP
        
        api-traitement # Code for conecting, getting infos for the Observe api

        media

        palangre-syc  # Code related to the Seychelles' longliners logbooks
        
        webapps # Code for the common parts 
        
        website # Where the specificities of development are
        
            media # temporary files - where the dropped logbooks are stocked before being send

            ...
