select distinct
    drug_key,
    min(drugname) as drugname
from
    {{ ref('stg_drug') }}
where drug_key is not null 
group by drug_key
