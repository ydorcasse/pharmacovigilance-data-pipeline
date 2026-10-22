select
    primaryid,
    caseid,
    try_cast(caseversion as integer) AS caseversion,
    try_strptime(event_dt, '%Y%m%d')::date AS event_dt,
    try_strptime(fda_dt, '%Y%m%d')::date AS fda_dt,
    try_cast(age as integer) AS age,
    age_cod,
    sex,
    occp_cod,
    occr_country
from read_csv(
    '../../../data/bronze/faers_ascii_2026q2/ASCII/DEMO26Q2.txt',
    delim = '$',
    header = true,
    all_varchar = true
)