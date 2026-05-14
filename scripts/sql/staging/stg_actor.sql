with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.actor` 
  )

  , final as (
    select
        actor_id
        , first_name as actor_first_name
        , last_name as actor_last_name
        , last_update as actor_last_update
   FROM base
  )

  select * from final
