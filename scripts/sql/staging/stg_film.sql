with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.film` 
  )

  , final as (
    select
          film_id
        , title as film_title
        , description as film_description
        , language_id as film_language_id
        , original_language_id as film_original_language_id
        , rental_duration as film_rental_duration
        , rental_rate as film_rental_rate
        , length as film_length
        , replacement_cost as film_replacement_cost
        , rating as film_rating
        , last_update as film_last_update
        , special_features as film_special_features
        , fulltext as film_fulltext
   FROM base
  )

  select * from final
