select distinct
    pt
from
    {{ ref('stg_reac') }}
where pt is not null