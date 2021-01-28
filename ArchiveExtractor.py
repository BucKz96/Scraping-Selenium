import os, os.path

# archive files
import zipfile
import rarfile
# Set to full path of unrar.exe if it is not in PATH
rarfile.UNRAR_TOOL = "unrar"

archive_extensions = [".rar", ".zip"]


"""
Parcours tous les dossiers et sous-dossier de root_folder
Pour chaque fichier archive trouvé, crée un dossier du nom de l'archive au même niveau de hiérarchie et extrait les fichiers à l'intérieur
Si des archives ont été extraites, recommence en traitant les nouvelles archives trouvées (cas d'archives dans des archives)
Si aucune nouvelle archive n'est trouvée, fin du script
return[0] = dossiers des archives trouvés lors de la première passe
return[1] = archives qui n'ont pas pû être extraites
"""
def extract_archive_files(root_folder):

	archive_files_processed = 0
	extraction_process_count = 0
	root_archives = []
	fails = []

	# OSX
	if os.name == 'posix':
		osx = True	

	# Windows
	if os.name == 'nt':
		osx = False

	while extraction_process_count == 0 or archive_files_processed > 0:

		archive_files_processed = 0

		print("processus d'extraction des fichiers de type archive : passe " + str(extraction_process_count + 1))

		for root, dirs, files in os.walk(root_folder):

			for file in files:

				filename, extension = os.path.splitext(file)

				if extension == ".zip":

					if osx:
						zip_filename = root + "/" + file
						zip_foldername = root + "/" + filename
					else:
						zip_filename = root + "\\" + file
						zip_foldername = root + "\\" + filename
					
					if not os.path.isdir(zip_foldername):

						try:

							zip_file = zipfile.ZipFile(zip_filename, 'r')
							zip_file.extractall(zip_foldername)
							zip_file.close()

							archive_files_processed += 1

						except:

							print("erreur lors de l'extraction de " + zip_filename)

							fails.append(zip_filename)

				if extension == ".rar":

					if osx:
						rar_filename = root + "/" + file
						rar_foldername = root + "/" + filename
					else:
						rar_filename = root + "\\" + file
						rar_foldername = root + "\\" + filename
					
					if not os.path.isdir(rar_foldername):

						try:

							rar_file = rarfile.RarFile(rar_filename, 'r')
							rar_file.extractall(rar_foldername)
							rar_file.close()

							archive_files_processed += 1

						except:

							print("erreur lors de l'extraction de " + rar_filename)

							fails.append(rar_filename)

		extraction_process_count += 1

		print(str(archive_files_processed) + " fichier(s) archive traité(s) / " + str(len(fails)) + " échec(s)")

	return root_archives, fails


def delete_archive_files(root_folder):

	# OSX
	if os.name == 'posix':
		osx = True	

	# Windows
	if os.name == 'nt':
		osx = False

	for root, dirs, files in os.walk(root_folder):

		for file in files:

			filename, extension = os.path.splitext(file)

			if extension in archive_extensions:

				if osx:
					zip_filename = root + "/" + file

				else:
					zip_filename = root + "\\" + file

				os.remove(zip_filename)