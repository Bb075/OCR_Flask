from flask import (
    Blueprint, flash, g, render_template, redirect, request, url_for, session, 
)
import os
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db
import magic
import subprocess
import json


bp = Blueprint('contract', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    contracts = db.execute(
        'SELECT id, idUser, date_issued, date_expires, nb_kids'
        ' FROM contract'
        ' ORDER BY date_expires'
    ).fetchall()
    return render_template('contract/index.html', contracts=contracts)

UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("Aucun fichier sélectionné")
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash("Aucun fichier sélectionné")
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            #convert_pdf_to_img(file.filename)
            #pseudo = g.user['username']
            ecrit = f"Fichier téléversé avec succès !"
            #convert_pdf_to_img(file.filename)
            call_OCR(file.filename)
            flash(ecrit)
            # verification du type de fichier 
            #
            # si pdf, alors exécution du script pour lancer OCR_V6.py si le type est un PDF sinon on passe a la suite -> appel de la fonction python3 pdf_to_img.py file.filename
            # si non, alors passe a la suite
            #
            #
            return redirect(url_for('contract.index'))
        else:
            flash("Type de fichier non autorisé. Les types autorisés sont : pdf, png, jpg, jpeg, gif")
            return redirect(request.url)
    return render_template('contract/upload.html')



def is_pdf(filename):
   mime = magic.Magic(mime=True)
   file_mime_type = mime.from_file(filename)
   return file_mime_type == "application/pdf"



def convert_pdf_to_img(pdf_file):
    path = "./" + pdf_file
    cmd = ['python3', 'pdf_to_img.py', path]
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print("Une erreur s'est produite :", e)
        print("Détails de l'erreur :")
        with open(path, 'rb') as file:
            print(file.read())

def call_OCR(filename):
    admin = g.user['username']
    try:
        # Exécute le script OCR_V6.py avec les arguments filename et nom d'utilisateur
        result = subprocess.run(['python3', 'OCR_V6.py', admin, filename], capture_output=True, check=True)
        json_data = f'data/{admin}.json'
        print("Contenu du fichier JSON:", json_data)

        with open(json_data, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("Données JSON:", data)

        if isinstance(data, list) and len(data) > 0:
            for item in data:
                # Insérez les données de chaque élément dans la base de données
                db = get_db()
                db.execute(
                'INSERT INTO contract (idUser, name, date_issued, date_expires, nb_kids, activate) VALUES (?, ?, ?, ?, ?, ?)',
                (session['user_id'], item['Nom'], item['Debut'], item['Fin'], item['Enfant'], True)
                )
                db.commit()
        else:
            print("Le fichier JSON ne contient pas une liste de données.")
        return
    except subprocess.CalledProcessError as e:
        # Gère les erreurs lors de l'exécution de la commande
        print("Une erreur s'est produite lors de l'exécution du script OCR_V6.py :", e)
    except ValueError as e:
        # Gère l'exception ValueError
        print("Une erreur de valeur est survenue :", e)
        raise  # Levez l'exception pour ne plus la voir sur le navigateur
    except Exception as e:
        # Gère les autres exceptions
        print("Une erreur s'est produite :", e)



def generate_json_file(file_client_name, nom, debut, fin, enfant):
    ocr_data = [
       {'id': 0,
        'Nom': nom,
        'Debut': debut,
        'Fin': fin,
        'Enfant': enfant}
    ]
    json_filename = file_client_name + ".json"
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(ocr_data, json_file)
    return json_filename



