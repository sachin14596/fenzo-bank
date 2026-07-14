{% snapshot accounts_snapshot %}

{{

    config(
        target_schema='dbt_dev',
        unique_key='account_id',
        strategy='check',
        check_cols=['tier','status']
    )

}}

select
    account_id,
    customer_id,
    account_type,
    currency,
    opened_at,
    status,
    tier
from {{ref('stg_fenzo_app__accounts')}}

{% endsnapshot %}