select
    d::date as date_day,
    extract(year from d) as year,
    extract(quarter from d) as quarter,
    extract(month from d) as month
from generate_series(
    date '2000-01-01',
    date '2027-12-31',
    interval '1 day'
) as dates(d)