select
    primaryid,
    caseid,
    outc_cod
from read_csv(
    '../../../data/bronze/faers_ascii_2026q2/ASCII/OUTC26Q2.txt',
    delim = '$',
    header = true,
    all_varchar = true
)