# Robotique

## Prérequis système
- **OS supportés** : Windows, macOS, Linux
- **Python** : Version 3.8 (64 bits obligatoire)
  - Téléchargez ici : [Python 3.8.6 (64-bit)](https://www.python.org/downloads/release/python-386/)
        Windows : https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe
        MacOS : https://www.python.org/ftp/python/3.8.6/python-3.8.6-macosx10.9.pkg



## Dépendances nécessaires
### Outils externes
- **CMake** : [Télécharger ici](https://cmake.org/download/)
- **ffmpeg** : [Télécharger ici](https://ffmpeg.org/download.html)

Lors de l'installation, il faudra ajouter au path pour pouvoir les appelés. 

## Installation (copier coller ces commandes dans le terminal de visual studio code[Terminal>Nouveau-terminal])
### macOS

python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


### Windows
py -3.8 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


## Modèles nécessaires
Certains scripts nécessitent des modèles d'intelligence artificielle. Téléchargez-les et placez-les dans le dossier `models`.

- **Reconnaissance vocale (`Speech_reco.py`)** :
  - [vosk-model-small-fr-0.22.zip](https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip)
- **Reconnaissance d'objets (`item_learning.py`, `item_detection.py`)** :
  - [efficientnet-lite1.tar.gz](https://storage.googleapis.com/cloud-tpu-checkpoints/efficientnet/lite/efficientnet-lite1.tar.gz)

## Structure des dossiers
```
extension_python/
├── Audio/
├── Battery/
├── models/                # Placez ici les modèles téléchargés
├── Reconnaissance/
├── Track/
└── README.md
```

## Exécution des scripts

Vous pouvez maintenant tester tous les scripts actuellement codés.

# Analyse des dossiers et fichiers du projet

## Dossier `Audio`

Le dossier `Audio` contient des scripts pour la gestion de l'audio, comme la reconnaissance vocale, la synthèse vocale, et la manipulation de fichiers audio.

#### `Speech reco.py`
- **Description** : Implémente une reconnaissance vocale en temps réel pour contrôler le robot RoboMaster.

#### `record.py`
- **Description** : Convertissent du texte en audio en utilisant `pyttsx3` et `ffmpeg`, la langue de la voix est défini par le langage par défault du système. 

#### `recordv2.py`
- **Description** : Convertissent du texte en audio en utilisant `pyttsx3` et `ffmpeg` avec voix text to speech customisable (français ou anglais) selon l'os. 

#### `Read-audio.py`
- **Description** : Lit un fichier audio sur le robot RoboMaster.

#### `set_volume.py`
- **Description** : Modifie le volume d'un fichier audio en utilisant `ffmpeg`.


## Dossier `Reconnaissance`

Le dossier `Reconnaissance` regroupe les scripts pour la reconnaissance visuelle, comme la reconnaissance d'objets, de visages, ou de couleurs.

### Sous-dossier `Item_Reco`

#### `item_learning.py`
- **Description** : Permet d'apprendre de nouveaux objets en capturant des images augmentées. Appuyez sur "l" une fois que l'objet est bien centré, entre le nom de l'objet dans le terminal puis dessinez les contours autour de l'objet que vous voulez(plusieurs clique via la souris). Pour augmenter la précision le script prendra plusieurs embendings avec plusieurs contraste, ce processus est actuellment configuré pour prendre 1m30 cependant il est possible de changer ce paramètre. Une fois l'objet appris, appuyez sur "enter" et fermez la page. 

#### `item_detection.py`
- **Description** : Détecte des objets appris en utilisant les embeddings générés.

### Sous-dossier `RoboMaster Reco`

#### `04_robot.py`
- **Description** : Détecte des robots dans le flux vidéo en utilisant le module de vision du SDK RoboMaster.

### Sous-dossier `Face_Reco`

#### `Face reco.py` (Necessite dlib [pip install dlib] cependant cette librairie est très instable, il se peut que ce script ne puisse pas marcher.)
- **Description** : Implémente une reconnaissance faciale en temps réel.
  - Lancez le script, appuyez sur `r` pour enregistrer un visage, entrez son nom dans le terminal, `q` pour quitter.


### Sous-dossier `Color_Reco` (Problème de contraste, le contraste de chaque robot n'est pas configuré de la même manière)

#### `color_reco.py`
- **Description** : Détecte la couleur dominante dans une zone centrale de l'image capturée.

## Dossier `Battery`

Le dossier `Battery` contient des scripts pour surveiller et gérer l'état de la batterie du robot.

## Dossier `Track`

Le dossier `Track` contient des scripts pour le suivi d'objets, de lignes, de personnes, de marqueurs, et de robots.

### Fichiers principaux

#### `line.py`
- **Description** : Suit une ligne de couleur spécifique.
  - Spécifiez la couleur de la ligne à suivre (rouge, vert, bleu, etc.).

#### `person.py`
- **Description** : Suit une personne détectée dans le flux vidéo.

#### `marker.py`
- **Description** : Suit un marqueur spécifique et ajuste la distance.

#### `robot.py`
- **Description** : Suit un autre robot détecté dans le flux vidéo, ajuste la vitesse et la direction pour maintenir le suivi, centre le robot dans le champ de vision.

#### `track_universal.py`
- **Description** : Implémente une fonction de suivi universelle pour détecter et suivre des cibles appris via `item_learning.py`.

## Dossier `models`

- **Description** : dossier où mettre les modèle d'intellegience artificielle. 