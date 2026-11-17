select
    primaryid,
    caseid,
    nullif(upper(trim(outc_cod)), '') as outc_cod
from read_csv(
    '../../../data/bronze/faers_ascii_*/ASCII/OUTC*.txt',
    delim = '$',
    header = true,
    all_varchar = true
)
