{{ config(materialized='table') }}

with

-- a : cas distincts par couple (médicament, réaction)
pair_counts as (
    select
        drug_key,
        reaction_key,
        count(distinct primaryid) as a
    from {{ ref('fact_adverse_event') }}
    group by drug_key, reaction_key
),

-- N_D : cas distincts mentionnant le médicament (toute réaction)
drug_totals as (
    select drug_key, count(distinct primaryid) as n_drug
    from {{ ref('fact_adverse_event') }}
    group by drug_key
),

-- N_R : cas distincts avec la réaction (tout médicament)
reaction_totals as (
    select reaction_key, count(distinct primaryid) as n_reaction
    from {{ ref('fact_adverse_event') }}
    group by reaction_key
),

-- N : total des cas distincts du périmètre d'analyse
grand_total as (
    select count(distinct primaryid) as n_total
    from {{ ref('fact_adverse_event') }}
),

-- le tableau 2x2 reconstruit à partir des 3 comptages
contingency as (
    select
        p.drug_key,
        p.reaction_key,
        p.a,
        d.n_drug     - p.a                          as b,
        r.n_reaction - p.a                          as c,
        g.n_total - d.n_drug - r.n_reaction + p.a   as d,
        d.n_drug,
        r.n_reaction,
        g.n_total
    from pair_counts p
    join drug_totals d      on p.drug_key = d.drug_key
    join reaction_totals r  on p.reaction_key = r.reaction_key
    cross join grand_total g
),

-- les métriques de disproportionnalité
metrics as (
    select
        drug_key,
        reaction_key,
        a, b, c, d,
        n_drug, n_reaction, n_total,
        (a::double / n_drug) / nullif(c::double / (c + d), 0)          as prr,
        (a::double * d) / nullif(b::double * c, 0)                     as ror,
        (n_total::double * pow((a::double * d) - (b::double * c), 2))
            / nullif((a + b)::double * (c + d) * (a + c) * (b + d), 0) as chi2
    from contingency
    where a >= 3
),

-- erreur-type du ln(ROR), puis intervalle de confiance à 95 %
ror_ci as (
    select
        *,
        exp(ln(ror) - 1.96 * se) as ror_lower,
        exp(ln(ror) + 1.96 * se) as ror_upper
    from (
        select
            *,
            sqrt( 1.0/nullif(a,0) + 1.0/nullif(b,0)
                + 1.0/nullif(c,0) + 1.0/nullif(d,0) ) as se
        from metrics
    )
)

select
    *,
    case when a >= 3 and ror_lower > 1 then true else false end as is_signal
from ror_ci
