# General
import os, os.path
import re
import time
import math
import json
from os import listdir
from os.path import isfile, join
import shutil
import logging

import sys
sys.path.append("../")

# Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import html
import html as htmllib
from html.parser import HTMLParser

# ODS format
from pyexcel_ods import save_data
from pyexcel_ods import get_data
from collections import OrderedDict

# Logs
from logger import Logger



class Scraper:
	"""Class use for scrapping website content"""

	load_imgs = True

	def __init__(self, export_dir="./exported_datas", download_dir="./downloads_product_pages", delay_after_loading=0.5):
		
		print("\nInitialisation de la classe 'Scraper'")
		print("chargement des images : " + str(self.load_imgs))

		self.homepage = ""

		self.delay_after_loading = delay_after_loading
		# création de l'objet logger qui va nous servir à écrire dans les logs
		self.logger = logging.getLogger()
		self.logger.setLevel(logging.INFO)
		# création d'un formateur qui va ajouter le temps, le niveau
		# de chaque message quand on écrira un message dans le log
		self.formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
		# création d'un handler qui va rediriger une écriture du log vers
		# un fichier en mode 'append', avec 1 backup et une taille max de 10Mo
		self.file_handler = logging.FileHandler('scraping.log', 'a')
		self.file_handler.setLevel(logging.INFO)
		self.file_handler.setFormatter(self.formatter)
		self.logger.addHandler(self.file_handler)

		# dossier de téléchargement des fichiers
		self.download_dir = re.sub("/$", "", download_dir)
		
		if not os.path.isdir(self.download_dir):
			os.mkdir(self.download_dir)

		print("Les fichiers seront téléchargés dans " + self.download_dir)
		Logger(log_info="Les fichiers seront téléchargés dans " + self.download_dir)
		# dossier de sauvegarde des datas
		self.export_dir = re.sub("/$", "", export_dir)

		if not os.path.isdir(self.export_dir):
			os.mkdir(self.export_dir)

		print("Les données récupérées seront enregistrées dans " + self.export_dir)
		Logger(log_info="Les données récupérées seront enregistrées dans " + self.export_dir)

		# charge ou non les images
		self.profile = webdriver.FirefoxProfile()
		if self.load_imgs == False:
			self.profile.set_preference('permissions.default.image', 2)
			self.profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

		# télécharge automatiquement les fichiers sans GUI
		self.profile.set_preference("browser.download.dir", self.download_dir)
		self.profile.set_preference("browser.download.folderList", 2); #This can be set to either 0, 1, or 2. When set to 0, Firefox will save all files on the user’s desktop. 1 saves the files in the Downloads folder and 2 saves file at the location specified for the most recent download.
		self.profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-compressed,application/x-zip-compressed,application/zip,application/pdf,image/jpeg,image/pjpeg,image/png,application/acad,image/vnd.dwg,image/x-dwg,application/dxf,image/vnd.dwg,image/x-dwg,application/x-koan,application/step,application/octet-stream");
		self.profile.set_preference( "browser.download.manager.showWhenStarting", False );
		self.profile.set_preference( "pdfjs.disabled", True );
		self.profile.set_preference("browser.link.open_newwindow", 3)
		self.profile.set_preference("browser.link.open_newwindow.restriction", 2)

		self.browser = webdriver.Firefox(self.profile)

		# start timer
		self.timeStart = time.time()


	def set_brand_name(self, brand_name):
		"""
		Nom que la marque prendra dans la base de données
		En même temps, défini les noms d'exportation des fichiers
		"""

		self.brand = brand_name
		# minuscule, sans espaces
		self.formated_brand_name = re.sub("\s", "_", brand_name.lower())
		self.file_path = self.export_dir + "/" + self.formated_brand_name


	def get_time_from_start_str(self):
		
        t = time.time() - self.timeStart
		return "{:10.2f}".format(t) + " seconde" + ("s" if t >= 2 else "") + " depuis le début du script"


	def close(self):

		# ferme Firefox
		self.browser.close()
		# get total time elapsed
		self.time_elapsed = self.get_time_from_start()
		print ("\nScript processed in: " + str(round(self.time_elapsed, 2)) + " seconds = " + str(round((self.time_elapsed/60), 2)) + " minute(s) = " + str(round((self.time_elapsed/3600), 2)) + " hour(s)")
		Logger(log_info="\nScript processed in: " + str(round(self.time_elapsed, 2)) + " seconds = " + str(round((self.time_elapsed/60), 2)) + " minute(s) = " + str(round((self.time_elapsed/3600), 2)) + " hour(s)")


	def remove_tags(self, text, tag_to_space):

		return re.sub("<[^>]*>", "" if tag_to_space == False else " ", text)
	

	def get_tag_content_as_string(self, node, tag_to_space=False, replace_br_with=""):

		result = str(html.tostring(node), "utf-8")
		if replace_br_with != "":
			result = re.sub("<br>", replace_br_with, result)
		result = self.remove_tags(result, tag_to_space)
		result = htmllib.unescape(result)
		result = self.remove_useless_spaces(result)
		return result


	def remove_end_line(self, string, replace_with_space=False):

		replace_pattern = " " if replace_with_space else ""
		result = self.remove_useless_spaces(result)
		return result


	def remove_semi_colon(self, string):

		result = re.sub(";", ".", string)
		return result


	def remove_useless_spaces(self, string):

		result = re.sub("\s{2,}", " ", string)
		result = re.sub("^\s|\s$", "", result) # first and last char
		return result
	

	def save_output(self, output_json_path, output_json, pretty_print=False):

		print("sauvegarde du fichier : " + output_json_path)
		outfile_file = open(output_json_path, "w")
		if pretty_print:
			outfile_file.write(json.dumps(output_json))
		outfile_file.close()


	def load_output(self, output_json_path):
		
		print("récupération des données à partir du fichier : " + output_json_path)
		outfile_file = open(output_json_path, "r")
		data = json.loads(outfile_file.read())
		outfile_file.close()
		return data


	def print_json(self, data, sort_keys=False):

		pretty_json = json.dumps(data, indent=4, sort_keys=sort_keys)
		return print(pretty_json)


	def download_wait(self, path_to_downloads):

		seconds = 0
		dl_wait = True
		while dl_wait and seconds < 20:
			time.sleep(1)
			dl_wait = False
			for fname in os.listdir(path_to_downloads):
				if fname.endswith('.part'):
					dl_wait = True
			seconds += 1
		return seconds


	def duplicate_product_by_measures(self, brand_name, with_complement=False):

		output_json_path = self.export_dir + "/" + brand_name.lower() + "_product_pages_data.json"
		new_product_list = []
		with open(output_json_path, "r+", encoding='utf-8') as json_file:
			data = json.load(json_file)
			for product in data:
				if len(product["measures"]) > 1:
					first_product_measures = product['measures'][0]
					new_product_original_measures_list = []
					new_product_original_measures_list.append(first_product_measures)
					for dict_measure in product["measures"][1:]:
						new_product_measures_list = []
						new_product_measures_list.append(dict_measure)
						new_product = product.copy()
						new_product['measures'] = new_product_measures_list
						if with_complement == False:
							new_product["product_name_complement"] = new_product["measures"][0]["size_raw"] 
						new_product_list.append(new_product)
					product['measures'] = new_product_original_measures_list
					if with_complement == False:
						product["product_name_complement"] = product["measures"][0]["size_raw"]
			print(len(new_product_list), "produit(s) dupliqué(s)")
			for new in new_product_list:
				data.append(new)
			json_file.seek(0)  # rewind
			json.dump(data, json_file, indent=4)
			json_file.truncate()


	def get_formatted_string(self, string):

		fstring = string.lower()
		fstring = re.sub("\s", "_", fstring)
		fstring = re.sub("à|â|ä|å", "a", fstring)
		fstring = re.sub("é|è|ê|ë", "e", fstring)
		fstring = re.sub("î|ï", "i", fstring)
		fstring = re.sub("ô|ö|ø", "o", fstring)
		fstring = re.sub("ù|ü", "u", fstring)
		fstring = re.sub("ñ", "n", fstring)
		fstring = re.sub("&", "and", fstring)
		fstring = re.sub("'|\"|\!|\?|\.|\:|\(|\)|\[|\]|\{|\}", "", fstring)
		fstring = re.sub("/|\\\\", "-", fstring)

		return fstring


	def load_page(self, url):

		try:
			print("\ncharge la page: " + url)
			self.browser.get(url) # navigate to the page
			time.sleep(self.delay_after_loading)
			self.get_dom()
		except:
			print("erreur au chargement de la page : " + url)
			Logger(log_error="erreur au chargement de la page : " + url)


	def get_dom(self):

		self.html = self.browser.execute_script("return document.body.innerHTML") #returns the inner HTML as a string
		self.dom = html.document_fromstring(self.html) #make HTML element object
    

	def Logger(log_info="", log_error=""):

		if log_info != "":
			self.logger.info(log_info)
		if log_error != "":
			self.logger.error(log_error)
		return