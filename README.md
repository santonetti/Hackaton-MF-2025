# Hackaton-MF-2025

### Observations et Projections Climatiques : Traitement et Visualisation

Ce dépôt contient des codes Python pour manipuler, analyser et visualiser des données météorologiques issues des observations SIM2 et de projections climatiques.
Les données sont organisées au format NetCDF, et des visualisations dynamiques sont proposées via une application web basée sur la librairie [Panel](https://panel.holoviz.org/).

#### Fonctionnalités

- Téléchargement et organisation des données météorologiques (SIM2 et projections climatiques). Les jeux de données utilisés sont indiqués dans la section des jeux de données réutilisés sur la page [Evaluation des biais sur des indicateurs climatiques - Hackathon MF 2025](https://www.data.gouv.fr/reuses/evaluation-des-biais-sur-des-indicateurs-climatiques-hackathon-mf-2025/)
- Traitement et réorganisation des fichiers au format NetCDF
- Calcul d'indicateurs à partir des variables climatiques (heat_index, TX35)
- Application interactive avec filtrage par année et par modèle climatique

---

### Installation de l’environnement avec `uv`

L’environnement Python est géré avec [uv](https://github.com/astral-sh/uv), pour une installation rapide et reproductible.

#### Prérequis

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) installé (`pip install uv`)

#### Installation

Dans le dossier du dépôt (où se trouve le fichier `uv.lock`) :

```shell
uv sync
```

---

### Application Panel en localhost

Une application à déployer en localhost a été mise en place avec la librairie Python Panel pour permettre de visualiser les données dynamiquement sur des graphiques contrôlés par des listes déroulantes. 

#### Déploiement
 
Pour déployer l'application :

```shell
panel serve app.py
```

Accessible sur l'URL : http://localhost:5006/app après déploiement

---

### Structure du dépôt

```shell
.
├── data/                # Données organisées
├── notebooks/           # Notebooks d’analyse
├── scripts/             # Scripts de traitement des données
├── app.py               # Application Panel principale
├── uv.lock              # Verrouillage des dépendances pour uv
└── README.md
```


---
