import os, os.path
import re
import json



json_path = "./ready_for_db/products_data.json"

json_file = open(json_path)
json_data = json.loads(json_file.read())
json_file.close()



# récupération des données

names = []
designers = []
urls = []

for product in json_data:

	if product["name"] is None:
		print("/!\\ Un produit n'a pas de nom")
		break

	names.append((product["name"], product["details"]))

	if product["designers"] is not None:
		for designer in product["designers"]:
			designers.append(designer)

	if product["brandWebsiteUrl"] is not None:
		urls.append(product["brandWebsiteUrl"])



# names

names = sorted(names)
unique_names = list(set(names))

print()
print(">> NAMES (total: " + str(len(names)) + ", uniques: " + str(len(unique_names)) + ")")

print()
print("{:30}{}".format("name", "detail"))
print("========================================")
for name in names:
	print("{:30}{}".format(name[0], name[1]))



# designers

designers = sorted(designers)
unique_designers = list(set(designers))

print()
print(">> DESIGNERS (total: " + str(len(designers)) + ", uniques: " + str(len(unique_designers)) + ")")

print()
for designer in unique_designers:
	print(designer)



# urls

unique_urls = list(set(urls))

print()
print(">> URLS (total: " + str(len(urls)) + ", uniques: " + str(len(unique_urls)) + ")")
