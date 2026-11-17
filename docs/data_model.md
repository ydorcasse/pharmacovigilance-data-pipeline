# Modèle de données — FAERS Pipeline

## Source
- Données : FDA FAERS, extraits trimestriels ASCII (format `$`-délimité)
- Périmètre : 4 trimestres (2025 Q3 → 2026 Q2)
- Par trimestre : 7 tables (DEMO, DRUG, REAC, OUTC, THER, INDI, RPSR) + un dossier `Deleted/` (caseid retirés par la FDA)

## Clés et relations (source)
- `primaryid` = clé de jointure universelle (= `caseid` + `caseversion`)
- `caseid` = identifiant stable du cas entre ses versions
- Relations 1-à-N : DEMO (1 cas) → DRUG / REAC / OUTC (plusieurs lignes)
- `role_cod` (DRUG) : PS (suspect principal), SS (suspect secondaire), C (concomitant), I (interagissant)

## Silver — staging (nettoyage, typage)
| Modèle      | Source   | Rôle |
|-------------|----------|------|
| stg_demo    | DEMO     | typage dates (`try_strptime`) et entiers (`try_cast`) |
| stg_drug    | DRUG     | clés normalisées `drug_key`, `active_ingredient_key` |
| stg_reac    | REAC     | clé normalisée `reaction_key` |
| stg_outc    | OUTC     | normalisation `outc_cod` (`upper(trim())`) |
| stg_deleted | Deleted/ | liste des `caseid` supprimés par la FDA |

Normalisation des clés : `nullif(lower(trim(...)), '')` → regroupe les variantes d'écriture (« ASPIRIN » / « aspirin ») sous une clé unique ; le vide devient NULL.

## Gold — dimensions
| Dimension             | Clé                   | Contenu |
|-----------------------|-----------------------|---------|
| dim_demo              | primaryid (grain caseid) | cas dédupliqué (version max), cas supprimés exclus ; age_years, age_group, sex, reporter_type, pays |
| dim_drug              | drug_key              | catalogue des produits (marque), y compris sans PA connu |
| dim_active_ingredient | active_ingredient_key | catalogue des principes actifs (séparé de la marque) |
| dim_reaction          | reaction_key          | termes MedDRA (pt) |
| dim_outc              | outc_cod              | 7 codes d'issue + libellé lisible |
| dim_date              | date_day              | calendrier généré (2000–2027) |

## Gold — faits
**fact_adverse_event** (factless fact)
- Grain : 1 ligne = (cas retenu × médicament suspect × réaction)
- Ne porte que des **clés** (primaryid, drug_key, active_ingredient_key, reaction_key, fda_dt), aucun nom brut
- Médicaments filtrés sur `role_cod ∈ {PS, SS}` ; périmètre des cas hérité de `dim_demo` via jointure ; dédupliqué (`select distinct`)

**fact_case_outcome** (factless fact)
- Grain : 1 ligne = (cas retenu × issue) — un cas peut avoir plusieurs issues
- Clés : primaryid, outc_cod

## Gold — mart analytique : signal_disproportionality
- Grain : 1 ligne = (drug_key × reaction_key)
- Tableau de contingence 2×2 sur **cas distincts** (primaryid) :
  a = cas avec médicament ET réaction · b = médicament sans réaction · c = réaction sans médicament · d = ni l'un ni l'autre
- Métriques : PRR, ROR + IC95 (`ror_lower`/`ror_upper`), chi²
- `is_signal` : critère standard (a ≥ 3 ET borne basse IC95 du ROR > 1)
- **Dénominateur N** : nombre de cas distincts présents dans `fact_adverse_event` (cas retenus ayant ≥ 1 médicament suspect et ≥ 1 réaction) — PAS l'ensemble de FAERS. Choix explicite.

## Règles de nettoyage (silver)
- Déduplication : `max(caseversion)` par `caseid` (QUALIFY row_number)
- Exclusion des cas supprimés par la FDA (anti-join sur `stg_deleted`) : 4 152 cas retirés sur les 4 trimestres
- Typage des dates `YYYYMMDD` → `date` (`try_strptime`, NULL si invalide/partielle)
- Normalisation des libellés en clés (`drug_key`, `active_ingredient_key`, `reaction_key`)
- Filtre `role_cod ∈ {PS, SS}` pour le lien médicament suspect → réaction

## Portée scientifique et limites (IMPORTANT)
- FAERS = **déclarations spontanées**, pas des cas confirmés ni une cohorte.
- La disproportionnalité génère des **hypothèses de signal**, jamais une preuve de causalité, de risque ou d'incidence.
- Biais connus : sous-déclaration, biais médiatiques/juridiques, clusters de déclaration (litiges, rappels, dispositifs), polymédication co-déclarée.
- Métriques instables sur petites cellules → interprétation conditionnée à un **support minimum** (a, n_drug, n_reaction) et à une **revue humaine**.

## Décisions clés
- Format ASCII (vs SGML) : plus simple à parser
- dbt + DuckDB ; tests dbt (unicité des clés, intégrité référentielle, grain des faits)
- Séparation marque (`dim_drug`) / principe actif (`dim_active_ingredient`)
- Disproportionnalité portée sur `drug_key` ; variante possible sur `active_ingredient_key`
- THER et INDI : hors modèle principal (raffinements futurs)

## Observations de qualité des données
- `age`/`age_cod` souvent nuls ensemble → `age_years = NULL` quand l'unité est inconnue (choix conservateur)
- `occp_cod` réel ≠ doc FAERS (présence de `HP`, absence de `OT`) ; forte part de déclarants inconnus
- `fda_dt` : quelques dates aberrantes → NULL via `try_strptime`, ignorées par les tests `relationships`