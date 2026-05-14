with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.country` 
  )

  , final as (
    select
          country_id
        , country 
        , last_update as country_last_update
   FROM base
  )

  select * from final
