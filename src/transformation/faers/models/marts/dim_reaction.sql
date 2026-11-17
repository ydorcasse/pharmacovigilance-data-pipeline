select distinct
    reaction_key,
    min(pt) as pt
from
    {{ ref('stg_reac') }}
where reaction_key is not null
group by reaction_key