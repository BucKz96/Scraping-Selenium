from os import listdir
import re
import json
from Scraper import *

scraper = Scraper()

brand_name = "VERPAN"

new_json = []

# new_format = {
#     "name": product name
#     "details": component name
#     "collection": collection name
#     "type": string
#     "designers": string[],
#     "description": string,
#     "brandWebsiteUrl": string
#     "width": int en mm,
#     "height": int en mm,
#     "depth": int en mm,
#     "seatHeight": int en mm,
#     "diameter": int en mm,
#     "weight": int en g,
#     "designedDate": année 4 chiffres,
#     "thumbnail": string,
#     "sourceFiles": string[]
# }
# value of type
# - Furniture
# - Lighting
# - Material
# - Accessory

input_data_json = "./exported_datas/{}_product_pages_data.json".format(brand_name.lower())
output_data_json = "./ready_for_db/products_data.json"

with open(input_data_json) as input_json:
	input_data = json.load(input_json)
	input_data = {x['url_product_page']:x for x in input_data}.values()
	input_data = sorted(input_data, key=lambda k: k['product_name'])
	count_to_add = 0

	for product in input_data: #[5:16]

		new_format = {}

		# Recupère les paths des fichiers
		sourceFiles = []
		formatted_name = product["product_name"]
		formatted_name = scraper.get_formatted_string(formatted_name)
		path_downloads_files = "./downloads_product_pages/{}/".format(formatted_name)
		for path, subdirs, files in os.walk(path_downloads_files):
			for name_file in files:
				if re.search(r'\.DS_Store$', name_file):
					pass
				else:
					sourceFiles.append(os.path.join(path, name_file))

		thumbnail = product["thumbnail"].split('/')[-1]
		if re.search(r'\?', thumbnail):
			thumbnail = re.sub(r'\?.*', '', thumbnail)
		thumbnail = path_downloads_files + thumbnail

		# Récupère la categorie pour attribuer un type au produit
		category = product["categories"]

		lighting_categorys = ["Pendants", "XL Pendants", "Table Lamps", "Floor Lamps", "Wall Lamps"]

		if category in lighting_categorys:
			type_item = "Lighting"
		else:
			type_item = "Furniture"
		
		# Recupère les informations du produit
		
		already_exists = False
		already_exists_second_name = False
		same_product = False
		count_match = 0
		count_match_second_name = 0
		count_same_product = 0

		for product_check in input_data:

			product_check_complement = ""
			product_complement = ""
			product_check_reference = product_check["brand_reference_name"]
			product_reference = product["brand_reference_name"]

			product_check_name = product_check["product_name"]
			product_check_complement = product_check["product_name_complement"]
			product_check_category = product_check["categories"]


			product_name = product["product_name"]
			product_complement = product["product_name_complement"]
			product_category = product["categories"]

			if product_check_name.lower() == product_name.lower():
				count_match += 1
				if count_match > 1:
					already_exists = True

			if product_check_complement != "" and product_complement != "":
				if product_check_name.lower() == product_name.lower() and product_check_complement.lower() == product_complement.lower():
					count_match_second_name += 1
					if count_match_second_name > 1:
						already_exists_second_name = True
			
			if product_check_complement != "" and product_complement != "":
				if product_check_name.lower() == product_name.lower() and product_check_category == product_category and product_check_complement.lower() == product_complement.lower():
					count_same_product += 1
					if count_same_product > 1:
						same_product = True
			else:
				if product_check_name.lower() == product_name.lower() and product_check_category == product_category:
					count_same_product += 1
					if count_same_product > 1:
						same_product = True
					
			# if len(product_check['product_name'].split()) > 1 and len(product['product_name'].split()) > 1:
			# 	product_check_second_name = product_check["product_name"].split()[1].lower()
			# 	product_second_name = product["product_name"].split()[1].lower()
			# 	if product_check_name == product_name and product_check_second_name == product_second_name:
			# 		count_match_second_name += 1
			# 		if count_match_second_name > 1:
			# 			already_exists_second_name = True

		if product_complement != "":
			details = product_complement
			name = product_name
		else:
			details = ""
		
		if same_product:
			count_to_add += 1

		if already_exists:	
			
			if product_complement != "":
				details = product_complement
				name = product_name
			elif same_product:
				details = category
				name = product_name
			else:
				details = category
				name = product_name
			
					
		else:
			details = ""
			name = product_name

		if details == "":
			details = None

		try:
			collection = product["collection"]
		except: collection = product["collections"]
		if collection == "":
			collection = None

		try:
			designer = product["designer"]
		except: designer = product["designers"]
		if designer == "":
			designers = None
		else:
			designers = []
			designers.append(designer)

		description = "".join(product["descriptions"])
		if description == "":
			description = None

		brandWebsiteUrl = product["url_product_page"]

		try:
			width = product["measures"]["width"]
		except: width = None

		try:
			height = product["measures"]["height"]
		except: height = None

		try:
			depth = product["measures"]["depth"]
		except: depth = None

		try:
			seatHeight = product["measures"]["seat_height"]
		except: seatHeight = None

		try:
			diameter = product["measures"]["diameter"]
		except: diameter = None

		try:
			weight = product["measures"]["weight"]
		except: weight = None

		designedDate = product["conception_year"].replace('ca.', '')
		if designedDate == "":
			designedDate = None
		else:
			if re.search(r'\/', designedDate):
				designedDate = designedDate.split('/')[0]
			if re.search(r'-', designedDate):
				designedDate = designedDate.split('-')[0]

			designedDate = int(designedDate)

		new_format.update({
			"name": name,
			"details": details,
			"collection": collection,
			"type": type_item,
			"designers": designers,
			"description": description,
			"brandWebsiteUrl": brandWebsiteUrl,
			"width": width,
			"height": height,
			"depth": depth,
			"seatHeight": seatHeight,
			"diameter": diameter,
			"weight": weight,
			"designedDate": designedDate,
			"thumbnail": thumbnail,
			"sourceFiles": sourceFiles
		})

		new_json.append(new_format)

with open(output_data_json, 'w') as output_json:
    json.dump(new_json, output_json, indent=4)

		

