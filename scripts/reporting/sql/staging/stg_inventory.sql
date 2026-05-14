with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.inventory` 
  )

  , final as (
    select
          inventory_id
        , film_id as inventory_film_id
        , store_id as inventory_store_id
        , last_update as inventory_last_update
   FROM base
  )

  select * from final
