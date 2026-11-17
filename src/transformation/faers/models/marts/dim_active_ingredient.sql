select
    active_ingredient_key,
    min(trim(prod_ai)) as active_ingredient_name
from {{ ref('stg_drug') }}
where active_ingredient_key is not null
group by active_ingredient_key
