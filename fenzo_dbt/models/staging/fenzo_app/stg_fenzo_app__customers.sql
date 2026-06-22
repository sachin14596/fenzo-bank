with source as (

    select * from {{ source('fenzo_app', 'customers') }}

),

renamed as (

    select
        customer_id,
        full_name,
        email,
        CAST(date_of_birth AS DATE) as date_of_birth,
        CAST(signup_date AS DATE)   as signup_date,
        country
    from source

),

final as (

    select * from renamed

)

select * from final