with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.language` 
  )

  , final as (
    select
          language_id 
        , name as language_name
        , last_update as language_last_update
   FROM base
  )

  select * from final
