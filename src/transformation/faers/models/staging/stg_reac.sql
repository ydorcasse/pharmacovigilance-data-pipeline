select
    primaryid,
    caseid,
    pt
from read_csv(
    '../../../data/bronze/faers_ascii_2026q2/ASCII/REAC26Q2.txt',
    delim = '$',
    header = true,
    all_varchar = true
)