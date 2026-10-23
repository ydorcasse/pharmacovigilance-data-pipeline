select distinct
    outc_cod
from
    {{ ref('stg_outc') }}
where outc_cod is not null