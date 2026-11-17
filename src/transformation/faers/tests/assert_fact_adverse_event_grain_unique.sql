-- Test singulier : le grain du fait principal doit être unique.
-- Grain = (cas retenu × médicament suspect × principe actif × réaction).
-- Un test singulier PASSE s'il renvoie 0 ligne ; ici il renvoie les
-- combinaisons dupliquées, donc toute ligne retournée = violation du grain.
select
    primaryid,
    drug_key,
    active_ingredient_key,
    reaction_key,
    count(*) as n
from {{ ref('fact_adverse_event') }}
group by 1, 2, 3, 4
having count(*) > 1
