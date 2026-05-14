with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.film_actor` 
  )

  , final as (
    select
          actor_id as film_actor_actor_id
        , film_id as film_actor_film_id
        , last_update as film_actor_last_update
   FROM base
  )

  select * from final
