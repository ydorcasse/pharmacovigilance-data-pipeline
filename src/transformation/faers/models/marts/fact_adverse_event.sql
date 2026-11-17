{{ config(materialized='table') }}

select distinct
    sd.primaryid,
    sd.drug_key,
    sd.active_ingredient_key,
    sr.reaction_key,
    dd.fda_dt
from {{ ref('stg_drug') }} as sd
join {{ ref('stg_reac') }} as sr
    on sd.primaryid = sr.primaryid
join {{ ref('dim_demo') }} as dd
    on sd.primaryid = dd.primaryid
where sd.role_cod in ('PS', 'SS')
    and sd.drug_key is not null
    and sr.reaction_key is not null
