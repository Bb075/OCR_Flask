#!/usr/bin/env python
# coding: utf-8

# # Import Libs

# In[1]:


from PIL import Image
import pytesseract
from pytesseract import Output
import cv2
import re
import sys
import time
import os
import json
start = time.time()


# # Recovery Of Entries Parameters

# In[2]:
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

#Vérification de la présence des deux paramètres (Exit si pas respecté)
if len(sys.argv) != 3:
    print("Usage: python OCR.py <Nom Prénom> <scan.png>")
    sys.exit(1)

#Récupération des valeurs des deux paramètres
param1 = sys.argv[1]
param2 = sys.argv[2]


# In[3]:


#Vérification de la présence des deux paramètres (Exit si pas respecté)
#Récupération des valeurs des deux paramètres
#param1 = "Docu Seb2"
#param2 = "test3.png"


# # Create Common Vars

# In[4]:


#Deux paramètres devront être pris en compte d'une quelconque manière
#Nom + Prénom de la personne en paramètre d'appel
#file_client_name='Andy Seb'
file_client_name= param1
#Chemin final des données clients
file_client_name_dir=os.getcwd()+"/data/"
file_client_name=file_client_name_dir+file_client_name
#selection de l'image
#source = 'test4.png'


# # OCR Treatment

# In[5]:


def ocr_treatment (param1,param2):
    source = param2
    img = cv2.imread(source)
    #essai noire et blanc
    #img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #zoom sur image pour une meilleur précision de l'OCR
    img = cv2.resize(img,None,fx=2,fy=2, interpolation = cv2.INTER_CUBIC)
    #récupération du texte en provenance de l'image avec choix du model de langage fra
    text=pytesseract.image_to_string(img, lang='fra')
    print(text)
    #écriture en sortie du texte
    with open("OCR_V3_output.txt", 'w', encoding='utf-8') as fichier:
        fichier.write(text)
    #découpage sous format de boîte du texte analysé par l'OCR pour avoir sa vision et savoir si la précision de l'ocr est plus ou moins bonne
    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    #affiche en sortie le compteur du nombre de boîte aillant un impacte sur la précision de l'ocr
    NbBox = len(d['level'])
    print ("Number of boxes: {}".format(NbBox))
    for i in range(NbBox):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        # display rectangle
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #crée une image avec la visibilité sur les cases
    cv2.imwrite('img.png', img)
    #Ouvre une fenêtre pour montrer le résultat en image mais bloque la suite du script
    #cv2.imshow('img', img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return text


# In[6]:


#text = ocr_treatment(param1,param2)


# # Recovery LastName Name AM/MA

# In[7]:


def extract_name_lname(file_client_name):
    #regex cherchant les noms et prénoms avec l'indicateur madame et nettoyage de l'output pour n'obtenir que le nom prénom
    pattern ="(Mme.*|Mms.*|mms.*|MME.*|madame.*|Madame.*|MADAME.*|Mr.*|MR.*|mr.*|Mrs.*|mrs.*|monsieur.*|Monsieur.*|MONSIEUR.*)"
    nom = re.findall(pattern, text)
    nom = str(nom)
    nom = re.sub(',.*', '', nom)
    pattern ="(Mme(.|\s)|Mms(.|\s)|mms(.|\s)|MME(.|\s)|madame(.|\s)|Madame(.|\s)|MADAME(.| )|Mr(.|\s)|MR(.|\s)|mr(.|\s)|Mrs(.|\s)|mrs(.|\s)|monsieur(.|\s)|Monsieur(.|\s)|MONSIEUR(.|\s)|\s\.\s|\.\s|\s.ounou)"
    nom = re.sub(pattern, '', nom)
    nom = nom.replace("[","").replace("'","").replace("(","").replace(")","").replace("[","").replace("]","").replace(" .","")
    print(nom)
    
    #écrit le résultat dans un fichier au nom de la personne à l'emplacement /data (les informations ajoutées seront traitées par l'api)
    with open(file_client_name+".txt", 'w', encoding='utf-8') as fichier:
        fichier.write(nom+'\n')
    return nom


# In[8]:


#nom = extract_name_lname(file_client_name)


# # Starting Agrement Date

# In[9]:


def start_approval(file_client_name):
    # Template de récupération des dates de début d'Agrément
    #01/09/2019 31/08/2024
    #RENOUVELLEMENT Date 06/02/2019
    pattern ="../../.....*../../...."
    debut = re.findall(pattern, text)
    debut = str(debut)
    debut = re.sub(',.*', '', debut)
    debut = debut.replace("[","").replace("'","").replace("(","").replace(")","").replace("[","").replace("]","").replace("œu ","").replace("au ","")
    print(debut)
    debut = re.sub("\s../../....", "", debut)
    print(debut)
    
    if debut=="":
        pattern ="RENOUVELLEMENT.*../../...."
        debut = re.findall(pattern, text)
        debut = str(debut)
        debut = re.sub(',.*', '', debut)
        debut = debut.replace("[","").replace("'","").replace("(","").replace(")","").replace("[","").replace("]","").replace("œu","").replace("au","").replace('"','').replace('"','').replace('-\s','').replace(':\s','')
        print(debut)
        debut = re.sub("RENOUVELLEMENT.*Date\s", "", debut)
        print(debut)
        with open(file_client_name+".txt", 'a', encoding='utf-8') as fichier:
            fichier.write(debut+'\n')
    else :
        with open(file_client_name+".txt", 'a', encoding='utf-8') as fichier:
            fichier.write(debut+'\n')
    return debut


# In[10]:


#debut = start_approval(file_client_name)


# # Ending Agrement Date

# In[11]:


def end_approval(file_client_name):
    # Template de récupération des dates de fin d'Agrément
    #01/09/2019 31/08/2024
    #ÉCHÉANCE DE L'AGRÉMENT Date - 05/02/2024
    pattern ="../../.....*../../...."
    fin = re.findall(pattern, text)
    fin = str(fin)
    fin = re.sub(',.*', '', fin)
    fin = fin.replace("[","").replace("'","").replace("(","").replace(")","").replace("[","").replace("]","").replace("œu ","").replace("au ","")
    print(fin)
    fin = re.sub("^../../....\s", "", fin)
    print(fin)
    
    if fin=="":
        pattern ="ÉCHÉANCE.*../../...."
        fin = re.findall(pattern, text)
        fin = str(fin)
        fin = re.sub(',.*', '', fin)
        fin = fin.replace("[","").replace("'","").replace("(","").replace(")","").replace("[","").replace("]","").replace("œu","").replace("au","").replace('"','').replace('"','').replace('- ','').replace(':\s','')
        print(fin)
        fin = re.sub("ÉCHÉANCE.*Date\s", "", fin)
        print(fin)
        with open(file_client_name+".txt", 'a', encoding='utf-8') as fichier:
            fichier.write(fin+'\n')
    else :
        with open(file_client_name+".txt", 'a', encoding='utf-8') as fichier:
            fichier.write(fin+'\n')
    return fin


# In[12]:


#fin = end_approval(file_client_name)


# # Simultaneous Children Number

# In[13]:


def number_of_children(file_client_name):
    # Template de récupération du nombre d'enfant simultané
    #Nombre d'enfants pouvant être accueillis simultanément : 4
    #- 1 enfant(s) de 0 à 3 an(s)
    pattern =".*enfant.*|.*ENFANT.*"
    enfant = re.findall(pattern, text)
    enfant = str(enfant)
    enfant = re.sub(',.*', '', enfant)
    enfant = enfant.replace("[","").replace("'","").replace("(","").replace(")","").replace("[","").replace("]","").replace('"','')
    print(enfant)
    #enfant = re.sub("^.*\:\s", "", x)
    enfant = re.findall(r'^\D*(\d+)', enfant)
    enfant = str(enfant)
    enfant = enfant.replace("['","").replace("']","")
    print(enfant)
    
    with open(file_client_name+".txt", 'a', encoding='utf-8') as fichier:
        fichier.write(enfant+'\n')
    return enfant


# In[14]:


#enfant = number_of_children(file_client_name)


# # Generate Json File

# In[15]:


def generate_json_file(file_client_name, nom, debut, fin, enfant):
    #Permet de gérérer les datas au format json
    ocr_data = [
       {'id': 0,
        'Nom': nom,
        'Debut': debut,
        'Fin': fin,
        'Enfant': enfant}
    ]
    
    with open(file_client_name+".json", 'w', encoding='utf-8') as json_file:
        json.dump(ocr_data, json_file)
    return


# In[16]:


#generate_json_file(file_client_name, nom, debut, fin, enfant)


# # Script Execution

# In[17]:


text = ocr_treatment(param1,param2)
nom = extract_name_lname(file_client_name)
debut = start_approval(file_client_name)
fin = end_approval(file_client_name)
enfant = number_of_children(file_client_name)
generate_json_file(file_client_name, nom, debut, fin, enfant)


# # Exec Time Of Script

# In[18]:


exec_time = time.time() - start
print(exec_time)

