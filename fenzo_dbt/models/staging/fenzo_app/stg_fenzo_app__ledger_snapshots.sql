with source as (

    select * from {{ source('fenzo_app', 'ledger_snapshots') }}

),

renamed as (

    select
        account_id,
        CAST(snapshot_date AS DATE) as snapshot_date,
        stated_balance_minor_units
    from source

),

final as (

    select * from renamed

)

select * from final