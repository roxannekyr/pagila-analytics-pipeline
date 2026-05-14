with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.customer` 
  )

  , final as (
    select
          customer_id
        , store_id as customer_store_id
        , first_name as customer_first_name
        , last_name as customer_last_name
        , email as customer_email
        , address_id as customer_address_id
        , activebool as customer_activebool
        , create_date as customer_create_date
        , last_update as customer_last_update
        , active as customer_active
   FROM base
  )

  select * from final
