-- Test fails if break rate exceeds 5% threshold
-- Returns rows when break rate is too high (should be empty for pass)

with break_summary as (

    select
        count(*) as total_snapshots,
        sum(is_break) as total_breaks,
        round(sum(is_break) / count(*) * 100, 2) as break_rate_pct
    from {{ ref('fct_reconciliation_breaks') }}

)

select *
from break_summary
where break_rate_pct > 5