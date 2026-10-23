select
    primaryid,
    caseid,
    caseversion,
    event_dt,
    fda_dt,
    age,
    age_cod,
    sex,
    occp_cod,
    occr_country
from 
    {{ ref('stg_demo') }}
qualify row_number() over (partition by caseid order by caseversion desc) = 1