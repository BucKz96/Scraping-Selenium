import urllib.request, urllib.parse
import ssl
import re
import os, os.path
import time

# Browser
from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess

# Logs
from Scraper import Logger




class FileDownloader:

	

	def __init__(self):

		print("Initialisation de FileDownloader")

		# éditables

		self.load_imgs = True
		self.time_between_downloads = 1.0

		# générés

		self.time_last_download = 0
		self.browser = None
		


	def get_ftime(self):

		return time.strftime("%Y-%m-%d %H:%M:%S")


	def release(self):

		if self.browser is not None:
			self.browser.close()



	def open_browser(self, download_dir):

		# lance le navigateur s'il n'est pas déjà ouvert

		if self.browser is not None:
			return

		self.profile = webdriver.FirefoxProfile()
		
		# charge ou non les images

		if not self.load_imgs:

			self.profile.set_preference('permissions.default.image', 2)
			self.profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

		# télécharge automatiquement les fichiers sans GUI

		self.profile.set_preference("browser.download.dir", download_dir)
		self.profile.set_preference("browser.download.folderList", 2); #This can be set to either 0, 1, or 2. When set to 0, Firefox will save all files on the user’s desktop. 1 saves the files in the Downloads folder and 2 saves file at the location specified for the most recent download.
		self.profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-compressed,application/x-zip-compressed,application/zip,application/pdf,image/jpeg,image/pjpeg,image/png,application/acad,image/vnd.dwg,image/x-dwg,application/dxf,image/vnd.dwg,image/x-dwg,application/x-koan,application/step,application/octet-stream");
		self.profile.set_preference( "browser.download.manager.showWhenStarting", False );
		self.profile.set_preference( "pdfjs.disabled", True );

		# lance le navigateur

		self.browser = webdriver.Firefox(self.profile)




	def download_url(self, url, download_dir, abs_path=False, with_curl=False) :


		print("===== Téléchargement d'un fichier " + self.get_ftime() + " =====")
		print("download_dir: " + download_dir)

		# nettoyage de l'url

		# vérifie que l'url du site n'ait pas été ajouté en trop au début de l'url
		if len(re.findall("https?://", url)) > 1:
			url = re.sub("^.*(?=https?://)", "", url)

		url = re.sub("\s", "%20", url)

		print("url: " + url)

		# délai

		delta_time = time.time() - self.time_last_download

		if delta_time < self.time_between_downloads:

			time.sleep( self.time_between_downloads - delta_time )

		self.time_last_download = time.time()

		# download

		if with_curl:

			self.download_with_curl(url, download_dir, abs_path)

		else:

			self.download_with_urllib(url, download_dir, abs_path)

		print()




	def download_with_curl(self, url, download_dir, abs_path):

		with_redirection = False

		url = url.replace(')', '%29').replace('(', '%28')

		# détecte si le fichier est derrière une redirection (A MODIFIER SELON L'URL CIBLE)
		if re.search(r'\.pdf$', url):
			with_redirection = True

		download_dir = re.sub(r'^\.', '', download_dir)
		if re.search(r'\.jpg[A-Z]', url):
			url = re.sub(r'\.jpg', '.jpg&', url)
		
		
		if with_redirection:
			# récupère le nom du fichier dans le header après la redirection d'url et stock la sortie de la commande (nom du fichier)
			file_name = subprocess.check_output("curl -sI {} | grep -o -E 'filename=.*$' | sed -e 's/filename=//'".format(url), shell=True)
			file_name = str(file_name)
			print("filenaaaaaaaaame", file_name)
			file_name = re.sub(r'^b\'\"', '', file_name)
			file_name = re.sub(r'\"\\r\\n\'', '', file_name)
			if file_name == "b''":
				file_name = url.split('/')[-1]
				file_name = file_name.replace('%20', ' ')
				print(file_name)
			
		else:
			file_name = os.path.basename(url)
			# supprime tout ce qui vient après l'extension du fichier
			file_name = re.sub(r"\?.*$", "", file_name)
			file_name = file_name.replace('%20', ' ')

		if file_name == "'b'" or file_name == "b":
			pass
			
		else:

			if abs_path:
				path_download_dir = download_dir

			else:

				# OSX
				if os.name == 'posix':
					path_download_dir = "{}{}".format(os.getcwd(), download_dir)

				# Windows
				if os.name == 'nt':
					path_download_dir = "{}{}".format(os.getcwd(), download_dir)

			dest_path = path_download_dir + "/" + file_name

			print("destination : " + dest_path)

			# télécharge le fichier uniquement s'il n'existe pas déjà
			if os.path.isfile(dest_path):
				print("Le fichier existe déjà")
				return
			
			directory = os.path.dirname(path_download_dir)
			if not os.path.exists(directory):
				os.makedirs(directory)

			url = re.sub(r'"\n"', '', url)

			# requête

			if with_redirection:
				# ajout de -L pour suivre la redirection d'url
				curl = subprocess.Popen(["curl", "-o", "{}".format(dest_path), "-L", "{}".format(url), "-w", "{}".format('%{http_code}')], stdout=subprocess.PIPE)
			else:
				curl = subprocess.Popen(["curl", "{}".format(url), "-o", "{}".format(dest_path), "-w", "{}".format('%{http_code}')], stdout=subprocess.PIPE)
			
			(out, err) = curl.communicate()
			http_code = re.search(r'^b\'(\d{1,3})\'', str(out)).group(1)
			if http_code == "200":
				print("OK : HTTP_CODE: {}".format(http_code))
			else:
				print('ERROR : HTTP_CODE: {}'.format(http_code))
				Logger(log_error=' CURL -- \nURL : {}\n DEST_PATH : {}\n HTTP CODE : {}\n'.format(url, dest_path, http_code))
				
			# curl = "curl {} -o {} -w {}".format(url, dest_path, '%{http_code}')
			# download = os.system(curl)




	def download_with_urllib(self, url, download_dir, abs_path):

		print("téléchargement avec urllib")

		# paramètres

		download_completed = False
		download_attempt = 0
		download_attempt_max = 3
		time_between_attempts = 3

		headers = {
			'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
		}

		# essaye de télécharger plusieurs fois le fichier si une erreur se produit

		while download_attempt < download_attempt_max and not download_completed:
			
			try:

				# requête

				req = urllib.request.Request(url, headers=headers)

				context = ssl._create_unverified_context()


				with urllib.request.urlopen(url, context=context) as response:

					# récupère le header de la réponse

					response_header = response.info()

					#print("response header: " + str(response_header))


					# déduit le nom de fichier

					basename = os.path.basename(url)

					url_filename = re.split("\?", basename)[0]


					# récupère directement le nom du fichier

					try:
						
						content_disposition = response_header["content-disposition"]
						values = re.split(";", content_disposition)

						for value in values:

							value = re.sub("^\s|\s$", "", value)

							split = re.split("=", value)

							if split[0] == "filename":

								filename = split[1]


					# ou déduit le nom du fichier

					except:

						# récupère le mime type du fichier
						
						mime = response_header["Content-Type"]

						print("mime: " + mime)

						# déduit l'extension

						mime_extensions = [
							{"mime":"application/pdf", "extension":".pdf"},
							{"mime":"application/zip", "extension":".zip"},
							{"mime":"image/jpeg", "extension":".jpg"}
						]

						extension = ""

						for case in mime_extensions:

							if case["mime"] == mime:

								extension = case["extension"]

								break

						if extension == "":

							extension = os.path.splitext(url_filename)[1]
							
							print("## use extension from url:" + extension)

						else:

							print("extension: " + extension)

						# nom assemblé

						filename = os.path.splitext(url_filename)[0] + extension


					# nettoyage de sécurité du nom de fichier

					filename = re.sub("^\"|\"$", "", filename)

					print("filename: " + filename)


					# chemin de destination

					if not os.path.isdir(download_dir):

							os.mkdir(download_dir)
					
					# OSX
					if os.name == 'posix':
						out_filename = download_dir + "/" + filename	

					# Windows
					if os.name == 'nt':
						out_filename = download_dir + "\\" + filename

					print("destination: " + out_filename)


					# sauvegarde le fichier

					if os.path.isfile(out_filename):

						download_completed = True

					else:

						response_data = response.read()

						out_file = open(out_filename, "wb")
						out_file.write(response_data)
						out_file.close()

						download_completed = True

						print("fichier téléchargé")
				

			
			# échec du téléchargement

			except:

				print("erreur au téléchargement du fichier")

				# supprimer le fichier qui a pu être partiellement téléchargé
				
				try:
					if os.path.isfile(out_file_name):
						os.remove(out_file_name)
				except:
					pass

				# attend avant de retenter le téléchargement

				download_attempt += 1

				if download_attempt < download_attempt_max:
					time.sleep(time_between_attempts)

				# toutes les tentatives ont échouées

				else:
					print("le fichier n'a pas pu être téléchargé")
					Logger(log_error=' URLLIB -- Erreur lors du téléchargement : \nURL : {}\n'.format(url))
