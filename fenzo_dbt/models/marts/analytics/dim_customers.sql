with source as(
    select * from {{ref('stg_fenzo_app__customers')}}
),

final as(

    select
        customer_id,
        full_name,
        email,
        date_of_birth,
        signup_date,
        country
    from source
)
select * from final