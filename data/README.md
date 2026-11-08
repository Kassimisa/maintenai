# Données

Les données ne sont **pas** versionnées sur GitHub (voir `.gitignore`).

| Dossier | Contenu | Comment l'obtenir |
|---|---|---|
| `skab/` | Jeu de données SKAB (pompe à eau, 8 capteurs, anomalies étiquetées) | `python scripts/download_skab.py` |
| `manuals/` | Manuels techniques PDF pour l'assistant IA | À ajouter à la main (droits de réutilisation vérifiés) |
| `index/` | Index vectoriel des manuels | `python -m maintenai.assistant.ingest` |

## Sources

| Dataset | Usage | Licence | Lien |
|---|---|---|---|
| **SKAB** | Construire et évaluer le détecteur | GPL-3.0 | https://github.com/waico/SKAB |
| **MetroPT-3** | Validation sur une vraie machine (compresseur, 6 mois, 4 vraies pannes) | CC BY 4.0 | https://archive.ics.uci.edu/dataset/791/metropt+3+dataset |
| **AI4I 2020** | Classification des types de panne (synthétique, sans horodatage) | à vérifier | https://archive.ics.uci.edu/dataset/601 |

## Critères d'une bonne donnée pour la détection d'anomalies

1. Horodatage de chaque mesure
2. Une seule machine identifiée par série
3. Mesures régulières et continues
4. Plusieurs capteurs pertinents (vibration, température, courant, pression, débit)
5. Longue période de fonctionnement normal
6. Quelques anomalies étiquetées pour l'évaluation

Bonus : historique de maintenance, contexte de fonctionnement, unités des capteurs.

## Données client

Les données des pilotes industriels sont **confidentielles** : ne jamais les placer dans ce dépôt.
