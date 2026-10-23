{{ config(materialized='table') }}

select
    sd.primaryid,
    sd.drugname,
    sd.prod_ai,
    sr.pt as reaction_pt
from {{ ref('stg_drug') }} as sd
join {{ ref('stg_reac') }} as sr
    on sd.primaryid = sr.primaryid
join {{ ref('dim_demo') }} as dd
    on sd.primaryid = dd.primaryid
where sd.role_cod in ('PS', 'SS')