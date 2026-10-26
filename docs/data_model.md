# Modèle de données — FAERS Pipeline

## Source
- Données : FDA FAERS, extract trimestriel ASCII (format `$`-délimité)
- Trimestre : 2026 Q2 (le plus récent disponible)
- 7 tables : DEMO, DRUG, REAC, OUTC, THER, INDI, RPSR + docs (Readme, ASC_NTS)

## Clés et relations
- `primaryid` = clé de jointure universelle (= `caseid` + `caseversion`)
- Relations 1-à-N : DEMO (1 cas) → DRUG / REAC / OUTC / INDI / THER (plusieurs)
- Deux grains source : le *cas* ; le *médicament dans le cas* (`drug_seq`)
- THER et INDI se rattachent à un médicament précis (via `drug_seq`), pas au cas

## Modèle cible : star schema
Table de faits **factless** : `fact_adverse_event`
- Grain : 1 ligne = (cas × médicament suspect × réaction)
- Ne porte pas de mesure → on compte les occurrences (base pour PRR, ROR, Chi²)
- Clé de rattachement : `primaryid`

Dimensions :
| Dimension      | Source | Contenu                                   |
|----------------|--------|-------------------------------------------|
| dim_drug       | DRUG   | médicament (filtré role_cod ∈ PS, SS)     |
| dim_reaction   | REAC   | réaction (pt, terme MedDRA)               |
| dim_demo       | DEMO   | age, sex, occp_cod, occr_country          |
| dim_outc       | OUTC   | code d'issue (DE, HO, LT…)                |
| dim_date       | généré | depuis event_dt / fda_dt (jour/mois/trim) |

## Règles de nettoyage (silver)
- Déduplication : garder `max(caseversion)` par `caseid`
- Exclure les cas supprimés (dossier `Deleted/`)
- Parser les dates `YYYYMMDD` (peuvent être partielles/incomplètes)
- Normaliser `drugname` (nom validé vs verbatim, cf. `val_vbm`)
- Filtrer `role_cod` sur PS/SS pour le lien médicament → réaction

## Décisions clés
- Format ASCII (vs SGML) : plus simple à parser
- dbt + DuckDB pour silver/gold
- THER et INDI : hors modèle principal pour l'instant (raffinements futurs)

## Observations de qualité des données

- `age` et `age_cod` sont toujours nuls ensemble (~37 % des cas sans âge).
  → age_years = null quand l'unité est inconnue (choix conservateur).
- `occp_cod` réel ≠ doc FAERS : présence de `HP`, absence de `OT`.
  ~72 % des déclarants sont inconnus (valeur vide).
- `fda_dt` : quelques dates aberrantes hors trimestre (2 lignes en 2025 Q4
  dans l'extrait 2026 Q2).
- Règle de dédup : max(caseversion) par caseid (1 doublon retiré sur Q2).