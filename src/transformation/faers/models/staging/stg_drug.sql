select
    primaryid,
    caseid,
    try_cast(drug_seq as integer) as drug_seq,
    role_cod,

    -- noms déclarés (bruts, pour l'affichage)
    drugname,
    prod_ai,

    -- clés normalisées : minuscules + sans espace superflus; vide -> NULL
    nullif(lower(trim(drugname)), '') as drug_key,
    nullif(lower(trim(prod_ai)), '') as active_ingredient_key,
from read_csv(
    '../../../data/bronze/faers_ascii_*/ASCII/DRUG*.txt',
    delim = '$',
    header = true,
    all_varchar = true
)
