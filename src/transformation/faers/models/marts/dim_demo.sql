with deduped as (

    select
        primaryid,
        caseid,
        caseversion,
        event_dt,
        fda_dt,
        age,
        age_cod,
        case
            when age_cod = 'DEC' then age * 10
            when age_cod = 'YR' then age
            when age_cod = 'MON' then age / 12.0
            when age_cod = 'WK' then age / 52.0
            when age_cod = 'DY' then age / 365.0
            when age_cod = 'HR' then age / 8_760.0
            else null
        end as age_years,
        case sex
            when 'M' then 'Male'
            when 'F' then 'Female'
            else 'Unknown'
        end as sex,
        case occp_cod
            when 'MD' then 'Physician'
            when 'PH' then 'Pharmacist'
            when 'HP' then 'Other health professional'
            when 'LW' then 'Lawyer'
            when 'CN' then 'Consumer'
            else 'Unknown'
        end as reporter_type,
        occr_country
    from 
        {{ ref('stg_demo') }}
    qualify row_number() over (partition by caseid order by caseversion desc) = 1
)

select
    *,
    case 
        when age_years < 18 then '0 - 17'
        when age_years < 65 then '18 - 64'
        when age_years >= 65 then '65+'
        else 'Unknown'
    end as age_group
from deduped