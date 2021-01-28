# Scraping-Selenium
Dossier modèle scraping avec selenium : 

Files :

- __Scraper.py__ ==> Classe principale du scraping (paramètres, fonctions utiles au bon déroulement du scraping).

- __FileDownloader.py__ ==> Classe qui permet de télécharger les fichiers liés aux produits (image, fichier 3D...).

- __ArchiveExtractor.py__ ==> Classe qui permet d'extraire les dossiers compressés et de les supprimer par la suite (.zip, .rar...).

- __logger.py__ ==> Script qui sort un fichier scraping.log.

- __nomdelamarque_product_pages_scraper.py__ ==> Script a modifier pour chaque marque selon les données a récupérer (image, dimensions, prix...), ouput en JSON.

- __product_data_checker.py__ ==> Script qui check (doublons, données manquantes...) les données récupérées du fichier JSON /exported_datas/nomdelamarque_product_pages_data.json.

- __nomdelamarque_ready_for_db_formatter.py__ ==> Script qui prend en input le fichier ./exported_datas/nomdelamarque_product_pages_data.json et en output le fichier ./ready_for_db/products_data.json afin d'avoir des données propres et prêtes a être envoyées dans la DB.

Directory :

- __/downloads_product_pages__ ==> C'est ici que les données téléchargées via nomdelamarque_product_pages_scraper.py seront stockées (images, fichier..) rangés par sous-dossiers portant le nom du produit.

- __/exported_datas__ ==> L'output JSON du script nomdelamarque_product_pages_scraper.py est rangé ici sous le nom nomdelamarque_product_pages_data.json.

- __/ready_for_db/__
  - __/ready_for_db/products_data.json__ ==> L'output JSON de nomdelamarque_ready_for_db_formatter.py sera stocké ici et prêt a être envoyé dans la DB.
  - __/ready_for_db/images__ ==> Les thumbnails (miniatures) des produits sont stockées dans ce dossier sous différents sous-dossiers portant le nom du produit afin d'être envoyé dans la DB.
  - __/ready_for_db/brand_data.json__ ==> JSON a renseigner manuellement avec différentes informations de la marque pour la DB.
