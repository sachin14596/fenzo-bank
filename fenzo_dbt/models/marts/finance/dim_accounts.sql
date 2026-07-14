with source as(
    select * from {{ref('stg_fenzo_app__accounts')}}
),

final as(
    select
        account_id,
        customer_id,
        account_type,
        currency,
        opened_at,
        DATE(opened_at) as opened_date,
        status,
        tier
    from source
)
select * from final