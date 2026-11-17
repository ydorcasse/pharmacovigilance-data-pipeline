select
    outc_cod,
    case outc_cod
        when 'DE' then 'Death'
        when 'OT' then 'Other Serious'
        when 'HO' then 'Hospitalization'
        when 'LT' then 'Life-Threatening'
        when 'DS' then 'Disability'
        when 'CA' then 'Congenital Anomaly'
        when 'RI' then 'Required Intervention'
    end as outcome_label
from
    {{ ref('stg_outc') }}
where outc_cod is not null
group by outc_cod