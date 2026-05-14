with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.staff` 
  )

  , final as (
    select
          staff_id
        , first_name as staff_first_name
        , last_name as staff_last_name
        , address_id as staff_address_id
        , email as staff_email
        , store_id as staff_store_id
        , active as staff_active
        , username as staff_username
        , password as staff_password
        , last_update as staff_last_update
        , picture as staff_picture
   FROM base
  )

  select * from final
