select
    primaryid,
    caseid,
    try_cast(drug_seq as integer) as drug_seq,
    role_cod,
    drugname,
    prod_ai
from read_csv(
    '../../../data/bronze/faers_ascii_*/ASCII/DRUG*.txt',
    delim = '$',
    header = true,
    all_varchar = true
)
