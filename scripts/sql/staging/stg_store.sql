with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.store` 
  )

  , final as (
    select
          store_id 
        , manager_staff_id as store_manager_staff_id
        , address_id as store_address_id
        , last_update as store_last_update
   FROM base
  )

  select * from final
