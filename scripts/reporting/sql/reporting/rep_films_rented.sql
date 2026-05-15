
with cte_rentals as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`
)
, cte_inventory as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_inventory`
)
, cte_film as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_film`
)
, cte_film_category as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_film_category`
)
, cte_category as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_category`
)
, cte_payment as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_payment`
)

, cte_film_lifespan as (
    select
        inv.inventory_film_id as film_id,
        cast(min(rent.rental_rental_date) as date) as first_rent,
        cast(max(rent.rental_rental_date) as date) as last_rent,
        date_diff(cast(max(rent.rental_rental_date) as date),
                  cast(min(rent.rental_rental_date) as date), month) as film_lifespan
    from cte_rentals as rent
    inner join cte_inventory as inv
        on rent.rental_inventory_id = inv.inventory_id
    group by inv.inventory_film_id
)

, cte_lifetime_revenue as (
    select
        category.category_id,
        category.category_name,
        film.film_id,
        film.film_title,
        count(distinct rent.rental_id) as total_unique_orders,
        sum(payment.payment_amount) as total_revenue
    from cte_rentals as rent
    left join cte_payment as payment
        on rent.rental_id = payment.payment_rental_id
            left join cte_inventory as inv
                on rent.rental_inventory_id = inv.inventory_id
                    left join cte_film as film
                        on inv.inventory_film_id = film.film_id
                            left join cte_film_category as film_category
                                on film.film_id = film_category.film_category_film_id
                                    left join cte_category as category
                                        on film_category.film_category_category_id = category.category_id
    where film.film_title not in ('GOODFELLAS SALUTE')
    group by category.category_id, category.category_name, film.film_id, film.film_title
)

select
    cte_lifetime_revenue.category_id,
    cte_lifetime_revenue.category_name,
    cte_lifetime_revenue.film_id,
    cte_lifetime_revenue.film_title,
    cte_film_lifespan.first_rent,
    cte_film_lifespan.last_rent,
    case when cte_film_lifespan.film_lifespan >= 12 then 'High-Performer'
         when cte_film_lifespan.film_lifespan >= 6  then 'Mid-Performer'
         else 'New'
    end as product_segment,
    cte_lifetime_revenue.total_unique_orders,
    cte_lifetime_revenue.total_revenue,
    round(cte_lifetime_revenue.total_revenue / nullif(cte_lifetime_revenue.total_unique_orders, 0), 2) as avg_order_revenue,
    case when cte_film_lifespan.film_lifespan = 0 then cte_lifetime_revenue.total_revenue
         else round(cte_lifetime_revenue.total_revenue / cte_film_lifespan.film_lifespan, 2)
    end as avg_monthly_revenue
from cte_lifetime_revenue
inner join cte_film_lifespan
    on cte_lifetime_revenue.film_id = cte_film_lifespan.film_id

order by cte_lifetime_revenue.film_id;

/*
---------------------------------------------------------------------------------------------------------------------------------------------------------------
PS: One row per film showing lifetime metrics, product segment, and category in order to be used as a dimension table related to rep_rental_details via film_id.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
*/
