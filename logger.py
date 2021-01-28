#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import logging
 
# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger()

logger.setLevel(logging.INFO)

# création d'un formateur qui va ajouter le temps, le niveau
# de chaque message quand on écrira un message dans le log
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# création d'un handler qui va rediriger une écriture du log vers
# un fichier en mode 'append', avec 1 backup et une taille max de 10Mo

file_handler = logging.FileHandler('scraping.log', 'a')

file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
    
def Logger(log_info="", log_error=""):

    if log_info != "":
        logger.info(log_info)
    if log_error != "":
        logger.error(log_error)

    return
