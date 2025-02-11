# -*- encoding: utf-8 -*-

import os
from flask import Flask
from flask_migrate import Migrate
from flask_minify import Minify
from apps.config import config_dict
from apps import create_app, db
import logging
from waitress import serve
import ftplib

# Fonction pour tester la connexion FTP
def testFTPConnection(host, username, password):
    try:
        with ftplib.FTP(host) as ftp:
            ftp.login(username, password)
            return True  # Connexion réussie
    except ftplib.all_errors as e:
        print(f"Erreur FTP: {e}")
        return False  # Connexion échouée

# Initialisation de l'application Flask
DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Charger la configuration
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production]')

app = create_app(app_config)

# Configuration de l'application
app.config['ENV'] = get_config_mode.capitalize()

# Initialisation des extensions
migrate = Migrate(app, db)
Minify(app=app, html=True, js=False, cssless=False)

# Commande pour tester la connexion FTP
@app.cli.command("test_ftp")
def test_ftp():
    host = "ftp.exemple.com"
    username = "utilisateur"
    password = "motdepasse"
    if testFTPConnection(host, username, password):
        app.logger.info('FTP connection OK')
    else:
        app.logger.info('FTP connection ERROR')

# Serveur de production avec Waitress si DEBUG est désactivé
if not DEBUG:
    serve(app, host='0.0.0.0', port=5000)
    print("PRODUCTION MODE")
else:
    app.logger.info(f'DEBUG = {DEBUG}')
    app.logger.info(f'Page Compression = {"FALSE" if DEBUG else "TRUE"}')
    app.logger.info(f'DBMS = {app_config.SQLALCHEMY_DATABASE_URI}')
    app.logger.info(f'ASSETS_ROOT = {app_config.ASSETS_ROOT}')

if __name__ == "__main__":
    # Configurez le logging
    logging.basicConfig(filename='log/app.log', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    with app.app_context():
        print(app.url_map)  # Affiche toutes les routes définies
        app.run(debug=DEBUG)
