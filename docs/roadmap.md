# Feuille de route

Calée sur les sessions de mentoring UM6P Explorer F26.

| Période | Business | Technique |
|---|---|---|
| **→ 10 nov. 2026** (session 2) | 3–5 entretiens clients, Lean Canvas mis à jour | Dépôt initial, détecteur SKAB de référence |
| **Novembre** | 15–20 entretiens, choix d'un secteur prioritaire | Assistant IA sur 3–5 manuels de pompes/compresseurs |
| **→ 8 déc. 2026** (session 3) | Early adopters nommés | Démo Streamlit : surveillance + assistant reliés |
| **Décembre** | Proposition de pilote à 1–2 usines | Validation sur MetroPT-3 (vraies pannes) ; autoencodeur |
| **→ 5 janv. 2027** (session 4) | Lettres d'intention, test de prix | Pilote : capteurs ESP32 + accéléromètre sur une machine |
| **Après Explorer** | Candidature financement, U-Founders | Comptes par usine, hébergement, app mobile |

## Prochaines améliorations techniques

- [ ] Validation sur MetroPT-3 (étiquettes créées à partir des dates de panne)
- [ ] Autoencodeur / LSTM et comparaison avec l'Isolation Forest
- [ ] Délai de détection : combien de secondes avant le début de l'anomalie
- [ ] Historique d'interventions consultable par l'assistant
- [ ] Explication des alertes (quel capteur a déclenché)
- [ ] Collecte terrain : ESP32 + MPU6050 / ADXL345 → MQTT → MaintenAI
