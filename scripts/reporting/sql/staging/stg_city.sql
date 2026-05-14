with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.city` 
  )

  , final as (
    select
          city_id
        , city as city_city
        , country_id as city_country_id
        , last_update as city_last_update
   FROM base
  )

  select * from final
