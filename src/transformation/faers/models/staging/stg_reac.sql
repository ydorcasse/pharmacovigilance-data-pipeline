select
    primaryid,
    caseid,
    pt
from read_csv(
    '../../../data/bronze/faers_ascii_*/ASCII/REAC*.txt',
    delim = '$',
    header = true,
    all_varchar = true
)