FROM debian:buster

WORKDIR /app_ocr

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/* && python3 -m pip install --upgrade pip
RUN pip install flask

# Mise à jour des paquets et installation de Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr


RUN pip install pytesseract
# Copie du fichier requirements.txt dans le conteneur

COPY requirements.txt /app/requirements.txt

# Installation des dépendances Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copie du code source dans le conteneur
COPY . /app_ocr

EXPOSE 8000

# Commande pour démarrer l'application Flask
CMD ["python3", "app_ocr.py"]





# # final configuration
# ENV FLASK_APP=app.py
# EXPOSE 8000
# CMD ["flask", "run", "--host", "
