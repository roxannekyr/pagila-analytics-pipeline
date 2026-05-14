with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.address` 
  )

  , final as (
    select
          address_id
        , address  as address_address
        , address2 as address_address2
        , district as address_district
        , city_id as address_city_id
        , postal_code as address_postal_code
        , phone as address_phone
        , last_update as address_last_update
   FROM base
  )

  select * from final
