# 🔧 MaintenAI

**Un copilote IA pour les techniciens de maintenance industrielle.**

MaintenAI aide les PME industrielles à réduire les arrêts imprévus :

1. **Détection d'anomalies** : le système apprend le fonctionnement normal d'une machine à partir de ses capteurs (vibration, courant, pression, température, débit) et lève une alerte quand le comportement s'en écarte, avant la panne.
2. **Assistant IA** : le technicien pose ses questions en français ; l'assistant répond pas à pas à partir des manuels techniques de l'usine et **cite ses sources** (fichier, page).
3. **Les deux sont reliés** : une alerte machine peut être transmise à l'assistant pour obtenir les vérifications recommandées.

> Projet de la **Team Kaizen** · programme **UM6P Explorer** (cohorte Fall 2026).

---

## Le problème

| | |
|---|---|
| ⚠️ Pannes imprévues | Maintenance surtout réactive : chaque arrêt bloque la production |
| 🐢 Diagnostic lent | Il dépend de quelques techniciens seniors |
| 📚 Documentation dispersée | Manuels papier, PDF, Excel, mémoire des équipes |

Détails business : [docs/lean_canvas.md](docs/lean_canvas.md) · Feuille de route : [docs/roadmap.md](docs/roadmap.md)

---

## Architecture

```
 Capteurs machine ──► Détection d'anomalies ──► Alerte
 (vibration, courant,   (Isolation Forest +         │
  pression, débit…)      fenêtres glissantes)       ▼
                                             Assistant IA (RAG) ◄── Manuels PDF indexés
                                             Ollama en local          (source + page)
                                                    │
                                                    ▼
                                         Interface Streamlit (démo)
```

```
maintenai/
├── app/streamlit_app.py        # démo : surveillance + assistant
├── maintenai/
│   ├── config.py               # chemins, capteurs, modèles Ollama
│   ├── anomaly/
│   │   ├── data.py             # chargement SKAB
│   │   ├── features.py         # moyennes / écarts-types glissants
│   │   ├── model.py            # AnomalyDetector (Isolation Forest + seuil)
│   │   └── train.py            # entraînement et évaluation
│   └── assistant/
│       ├── ollama_client.py    # API locale Ollama
│       ├── ingest.py           # PDF → morceaux → embeddings
│       └── rag.py              # recherche + réponse avec sources
├── scripts/
│   ├── download_skab.py        # télécharge le jeu de données
│   └── plot_experiment.py      # graphique d'une expérience
├── docs/                       # Lean Canvas, feuille de route
├── data/                       # données (non versionnées, voir data/README.md)
├── results/                    # métriques de référence
└── tests/
```

---

## Installation

Prérequis : Python 3.10+ et [Ollama](https://ollama.com) pour l'assistant.

```bash
git clone https://github.com/<votre-compte>/maintenai.git
cd maintenai
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/Mac : source .venv/bin/activate)
pip install -r requirements.txt
```

## Utilisation

### 1. Détection d'anomalies

```bash
python scripts/download_skab.py              # télécharge SKAB (~35 fichiers CSV)
python -m maintenai.anomaly.train            # entraîne et évalue
python scripts/plot_experiment.py valve1 0   # graphique d'une expérience
```

### 2. Assistant IA

```bash
ollama pull nomic-embed-text                 # modèle d'embeddings
ollama pull qwen3.5:9b                       # modèle de chat (ou un autre, voir plus bas)
# copiez des manuels PDF dans data/manuals/
python -m maintenai.assistant.ingest
python -m maintenai.assistant.rag "La pompe vibre anormalement, que vérifier ?"
```

Changer de modèle : variables d'environnement `MAINTENAI_CHAT_MODEL`, `MAINTENAI_EMBED_MODEL`, `OLLAMA_URL`.

### 3. Démo

```bash
streamlit run app/streamlit_app.py
```

### Tests

```bash
pytest
```

---

## Résultats actuels (référence)

Jeu de données : **SKAB** (pompe à eau, 8 capteurs, 34 expériences avec anomalies étiquetées).
Modèle : Isolation Forest, fenêtre glissante de 10 s, seuil au quantile 99 % des scores normaux.

| Protocole | Précision | Rappel | F1 | Taux de fausses alertes |
|---|---|---|---|---|
| **Par expérience** (apprend sur les 400 premières secondes, surveille la suite) | 0.73 | 0.50 | **0.59** | 0.21 |
| Global (un modèle appris sur l'enregistrement « anomaly-free ») | 0.38 | 0.94 | 0.54 | 0.84 |

**Ce qu'on en retient :**
- Apprendre le comportement normal **de chaque machine** donne de bien meilleurs résultats qu'un modèle unique : le « normal » change d'une installation à l'autre. C'est le mode de déploiement visé chez les clients.
- Ce n'est qu'une **référence de départ**. Pistes : autoencodeur, réglage du seuil, délai de détection (voir [docs/roadmap.md](docs/roadmap.md)).

Fichiers : [results/metrics_per-file.json](results/metrics_per-file.json), [results/metrics_global.json](results/metrics_global.json)

---

## Données

Voir [data/README.md](data/README.md) : sources (SKAB, MetroPT-3, AI4I), licences et critères d'une bonne donnée.
Les données des clients pilotes sont confidentielles et ne sont **jamais** versionnées.

## Équipe

**Team Kaizen** : [Prénom Nom] · Maryam ELALAMI

## Licence

À définir. Note : SKAB est distribué sous GPL-3.0 ; ce dépôt ne contient pas ses données, il les télécharge.
