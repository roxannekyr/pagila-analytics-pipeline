with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.film_category` 
  )

  , final as (
    select
          film_id as film_category_film_id
        , category_id as film_category_category_id
        , last_update as film_category_last_update
   FROM base
  )

  select * from final
