select distinct
    trim(caseid) as caseid
from read_csv(
    '../../../data/bronze/faers_ascii_*/Deleted/DELETE*.txt',
    header = false,
    names = ['caseid'],
    all_varchar = true
)
where nullif(trim(caseid), '') is not null
