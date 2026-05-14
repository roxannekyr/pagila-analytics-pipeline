with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.rental` 
  )

  , final as (
    select
          rental_id
        , rental_date as rental_rental_date
        , inventory_id as rental_inventory_id
        , customer_id as rental_customer_id
        , return_date as rental_return_date
        , staff_id as rental_staff_id
        , last_update as rental_last_update
   FROM base
  )

  select * from final
