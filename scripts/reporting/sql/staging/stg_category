with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.category` 
  )

  , final as (
    select
          category_id
        , name as category_name
        , last_update as category_last_update
   FROM base
  )

  select * from final
