{{ config(materialized='table') }}

select distinct
    so.primaryid,
    so.outc_cod
from {{ ref('stg_outc') }} as so
join {{ ref('dim_demo') }} as dd
    on so.primaryid = dd.primaryid
where so.outc_cod is not null
