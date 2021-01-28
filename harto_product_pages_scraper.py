# General
import os, os.path
import re
import time
import math
import json
from os import listdir
from os.path import isfile, join
import shutil
import urllib.request

import sys
import os.path
sys.path.append("../")

# Scraping
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from lxml import html
import html as htmllib
from Scraper import *

# download
from FileDownloader import *
from ArchiveExtractor import *



current_folder = os.path.dirname(os.path.realpath(__file__))

brand_name = "HARTÔ"

skip_web_scraping = False
download_files = True

output_json = []
output_json_path = current_folder + "/exported_datas/" + brand_name.lower() + "_product_pages_data.json"

# init the scraper
scraper = Scraper(export_dir = current_folder + "/exported_datas", download_dir = current_folder + "/downloads_product_pages")


# >>> données sur la marque ----------------------------------------------------------------------------------------------------

# nom qui sera utilisé dans la base de données
scraper.set_brand_name(brand_name)

# homepage du site à scraper
# parfois, les liens sont relatifs, il faut ajouter homepage + lien pour avoir l'url correcte
scraper.homepage = "https://www.hartodesign.fr/"

# première page à charger, pas forcément la homepage
scraper.load_page(scraper.homepage)

# <<< données sur la marque ----------------------------------------------------------------------------------------------------

# >>> scraping ----------------------------------------------------------------------------------------------------

if not skip_web_scraping:

	print("\n---------- Récupère les liens des pages produit ----------\n")

	categories = []

	category_container = scraper.dom.find('.//ul[@class="menu_1"]/li[1]/ul[@class="child"]')
	category_tags = category_container.findall('./li/a')
	
	for category_tag in category_tags:
		
		category_name = scraper.get_tag_content_as_string(category_tag)
		category_url = category_tag.get('href')
		categories.append({
			"name": category_name,
			"url": category_url
		})

	# récupère les produits

	products = []

	for i in range(len(categories)):
		
		# if i >= 1: break

		category = categories[i]
		scraper.print_json(category["name"])
		scraper.load_page(category["url"])


		products_container = scraper.dom.find('.//div[@class="category-products"]')
		product_tags = products_container.findall('.//li/div[@class="href"]')

		for product_tag in product_tags:

			prices = {}
			url_product_page = product_tag.find('./a').get('href')
			product_name = scraper.get_tag_content_as_string(product_tag.find('.//span[@class="nomProduit"]'))
			thumbnail = product_tag.find('./a/img').get("src")
			designer = scraper.get_tag_content_as_string(product_tag.find('.//span[@class="design-br"]'))
			prices_content = scraper.get_tag_content_as_string(product_tag.find('.//span[@class="price"]'))
			prices.update({
				"euros": prices_content.replace('\u00a0', ''),
				"euros_ttc": prices_content.replace('€', '').replace('\u00a0', '')
			})

			products.append({
				"brand": brand_name,
				"categories": category["name"],
				"product_type": "furniture",
				"product_name": product_name,
				"product_name_complement": "",
				"url_product_page": url_product_page,
				"thumbnail": thumbnail,
				"designers": designer,
				"prices": prices
			})
			
	scraper.print_json(products)

	# récupère les pages produits

	for i in range(len(products)):

		# if i >= 5: break

		product = products[i]

		scraper.load_page(product["url_product_page"])
		files_urls = []

		# DESCRIPTIONS
		descriptions = []
		try:
			description_tag = scraper.dom.find('.//div[@class="description-view"]/')
			if description_tag is not None:
				description = scraper.get_tag_content_as_string(description_tag)
				descriptions.append(description)
		except: pass

		# COLORS AND MATERIALS
		colors_and_materials = {}
		colors = []
		materials = []
		try:
			materials_container = scraper.dom.find('.//div[@class="cols-vi mat"]/p[@class="desc"]')
			if materials_container is not None:
				materials_content = scraper.get_tag_content_as_string(materials_container)
				if materials_content is not None or materials_content != "":
					materials.append(materials_content)
			colors_and_materials.update({
				"colors": colors,
				"materials": materials
			})
		except: pass

		# MEASURES
		measures = {}
		weight_raw = ""
		size_raw = ""
		height = ""
		width = ""
		depth = ""
		diameter = ""
		seat_height = ""
		weight = ""
		try:
			height_pattern = re.compile(r'(^H\d{1,}(\.\d{1,})?)')
			width_pattern = re.compile(r'(W\d{1,}(\.\d{1,})?)')
			depth_pattern = re.compile(r'(D\d{1,}(\.\d{1,})?)')
			diameter_pattern = re.compile(r'(dia\d{1,}(\.\d{1,})?)')
			seat_height_pattern = re.compile(r'(^SH\d{1,}(\.\d{1,})?)')
			weight_pattern = re.compile(r'(^WG\d{1,}(\.\d{1,})?)')

			sizes_tag = scraper.dom.find('.//div[@class="cols-vi dim"]/p[@class="desc"]')
			if sizes_tag is not None:
				size_raw = scraper.get_tag_content_as_string(sizes_tag)
				size_elems = size_raw.replace('cm', ' ').replace('.', '').replace('Longueur : ', 'D').replace('Longeur : ', 'D').replace('Longueur: ', 'D').replace('Largeur: ', 'W').replace('Largeur : ', 'W').replace('Hauteur totale: ', 'H').replace('Hauteur: ', 'H').replace('Hauteur : ', 'H').replace('Profondeur totale: ', 'D').replace('Hauteur d\'assise: ', 'SH').replace('Poids: ', 'WG').replace('Diamètre de la table: ', 'dia').replace('Diamètre de la table : ', 'dia').replace('Diamètre du plateau : ', 'dia')
				size_elems = size_elems.split(' ')

				for size_elem in size_elems:

					if height_pattern.search(size_elem) is not None:
						height = height_pattern.search(size_elem).group(1).replace('H', '')
						if re.search(r'\.', height):
							height = float(height) * 10
							height = int(height) 
						else:
							height = int(height) * 10
					if width_pattern.search(size_elem) is not None:
						width = width_pattern.search(size_elem).group(1).replace('W', '')
						if re.search(r'\.', width):
							width = float(width) * 10
							width = int(width) 
						else:
							width = int(width) * 10
					if depth_pattern.search(size_elem) is not None:
						depth = depth_pattern.search(size_elem).group(1).replace('D', '')
						if re.search(r'\.', depth):
							depth = float(depth) * 10 
							depth = int(depth) 
						else:
							depth = int(depth) * 10
					if diameter_pattern.search(size_elem) is not None:
						diameter = diameter_pattern.search(size_elem).group(1).replace('dia', '')
						if re.search(r'\.', diameter):
							diameter = float(diameter) * 10
							diameter = int(diameter) 
						else:
							diameter = int(diameter) * 10
					if seat_height_pattern.search(size_elem) is not None:
						seat_height = seat_height_pattern.search(size_elem).group(1).replace('SH', '')
						if re.search(r'\.', seat_height):
							seat_height = float(seat_height) * 10
							seat_height = int(seat_height) 
						else:
							seat_height = int(seat_height) * 10
					if weight_pattern.search(size_elem) is not None:
						weight = weight_pattern.search(size_elem).group(1).replace('WG', '')
						if re.search(r'\.', weight):
							weight = float(weight) * 1000
							weight = int(weight) 
						else:
							weight = int(weight) * 1000
		
				measures.update({
					"size_raw": size_raw,
					"weight_raw": weight_raw,
					"diameter": diameter,
					"width": width,
					"height": height,
					"depth": depth,
					"seat_height": seat_height,
					"weight": weight
				})
		except: pass

		# IMAGES GALLERY
		img_uniq_url = set()
		try:
			images_gallery_container = scraper.dom.find('.//div[@class="owl-stage"]')
			if images_gallery_container is not None:
				images_gallery_tags = images_gallery_container.findall('.//div[@class="item"]/img')
				for images_gallery_tag in images_gallery_tags:
					image_gallery_url = images_gallery_tag.get('src')
					if image_gallery_url is not None:
						img_uniq_url.add(image_gallery_url)
		except: pass

		# IMG SET
		for url in img_uniq_url:
			if re.search(r'^/', url):
				url = scraper.homepage + url
			files_urls.append(url)
		
		product.update({
			"url_download_page": "",
			"collections": "",
			"brand_reference_name": "",
			"designers": designer,
			"designers_description": "",
			"conception_year": "",
			"production_year": "",
			"measures": measures,
			"descriptions": descriptions,
			"files_urls": files_urls,
			"files_request_datas": "",
			"colors_and_materials": colors_and_materials,
			"variations": "",
			"lighting": "",
			"availability": "",
			"eshops": ""
		})

		scraper.print_json(product)
		output_json.append(product)

	# save
	
	scraper.save_output(output_json_path, output_json, pretty_print=True)

# si pas de téléchargement
if download_files == False:
	scraper.close()

# [START] téléchargement des fichiers ----------------------------------------------------------------------------------------------------

else:

	data = scraper.load_output(output_json_path)

	file_downloader = FileDownloader()

	print(str(len(data)) + " produit(s) scrapé(s)")

	for i in range(len(data)):

		# if i <= 906: continue
		
		product = data[i]
		
		if product["product_name_complement"] != "":
			formatted_name = product["product_name"] + " " + product["product_name_complement"]
		else:
			formatted_name = product["product_name"] 

		formatted_name = scraper.get_formatted_string(formatted_name) 

		if formatted_name == "":
			formatted_name = "_no_name"

		print("fname : " + formatted_name)

		dest_folder = re.sub("\\\\", "/", scraper.download_dir) + "/" + formatted_name

		if not os.path.isdir(dest_folder):
			os.mkdir(dest_folder)

		for files in product["files_urls"], product["thumbnail"]:
			if re.search(r'^\[', str(files)):
				for file in files:
					file_downloader.download_url(file, dest_folder, with_curl=True, abs_path=True)
			else:
				file_downloader.download_url(files, dest_folder, with_curl=True, abs_path=True)
	
	# unzip

	extract_archive_files(scraper.download_dir)

	delete_archive_files(scraper.download_dir)

	# fermeture
	
	file_downloader.release()
	scraper.close()

# [END] téléchargement des fichiers ----------------------------------------------------------------------------------------------------
