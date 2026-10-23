select distinct
    drugname,
    prod_ai
from
    {{ ref('stg_drug') }}
where 
    drugname is not null 
    and prod_ai is not null