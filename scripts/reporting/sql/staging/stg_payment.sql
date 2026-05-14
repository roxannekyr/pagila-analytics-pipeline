with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.payment` 
  )

  , final as (
    select
          payment_id
        , customer_id as payment_customer_id
        , staff_id as payment_staff_id
        , rental_id as payment_rental_id
        , amount as payment_amount
        , payment_date as payment_payment_date
   FROM base
  )

  select * from final
