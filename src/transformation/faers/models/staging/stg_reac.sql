select
    primaryid,
    caseid,
    pt,
    nullif(lower(trim(pt)), '') as reaction_key
from read_csv(
    '../../../data/bronze/faers_ascii_*/ASCII/REAC*.txt',
    delim = '$',
    header = true,
    all_varchar = true
)