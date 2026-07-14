-- Test fails if any current account has a negative balance
-- Returns rows that violate the assertion (should be empty for pass)
{{ config(severity='warn') }}

select
    b.account_id,
    b.balance_date,
    b.balance
from {{ ref('fct_account_balances') }} b
join {{ ref('dim_accounts') }} a
    on b.account_id = a.account_id
where a.account_type = 'current'
and b.balance < 0