-- Test singulier : le grain du factless fact doit être unique.
-- Grain = (cas retenu × issue).
select
    primaryid,
    outc_cod,
    count(*) as n
from {{ ref('fact_case_outcome') }}
group by 1, 2
having count(*) > 1
