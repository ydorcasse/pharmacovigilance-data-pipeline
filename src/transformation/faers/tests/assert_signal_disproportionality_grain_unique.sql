select drug_key, reaction_key, count(*) as n
from {{ ref('signal_disproportionality') }}
group by 1, 2
having count(*) > 1