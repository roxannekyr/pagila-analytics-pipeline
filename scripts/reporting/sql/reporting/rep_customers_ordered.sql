
    with cte_customers as (
        select *
        from `project-401f4646-3663-4125-aaa.staging_db.stg_customer`
    )
    , cte_rentals as (
        select * 
        from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`
    )

    /* Calculating customer_lifespan */
    , cte_customer_lifespan as (
        select
            rent.rental_customer_id as customer_id,
            date(min(rent.rental_rental_date)) as first_rent,
            date(max(rent.rental_rental_date)) as last_rent,
            date_diff(DATE(max(rent.rental_rental_date)), DATE(min(rent.rental_rental_date)), month) as customer_lifespan 
        from cte_rentals as rent
        group by rent.rental_customer_id
    )

    /* Calculating customer recency */
    , cte_customer_recency as (
        select
        rent.rental_customer_id as customer_id,date_diff((select date(max(rental_rental_date)) from cte_rentals),date(max(rental_rental_date)),month
        ) as recency
    from cte_rentals as rent
    group by rent.rental_customer_id
    )

    , cte_payment as (
        select * 
        from `project-401f4646-3663-4125-aaa.staging_db.stg_payment`
    )

    , cte_film as (
        select * 
        from `project-401f4646-3663-4125-aaa.staging_db.stg_film`
    )

    , cte_inventory as (
        select *
        from `project-401f4646-3663-4125-aaa.staging_db.stg_inventory`
    )

    , cte_address as (
    select *
    from `project-401f4646-3663-4125-aaa.staging_db.stg_address`
    )

    , cte_city as (
    select *
    from `project-401f4646-3663-4125-aaa.staging_db.stg_city`
    )

    , cte_country as (
    select *
    from `project-401f4646-3663-4125-aaa.staging_db.stg_country`
    )


    /* Lifetime totals per customer */
    , cte_lifetime_revenue as (
        select
            cte_country.country as country,
            cte_city.city_city as city,
            cte_customers.customer_id,
            concat(cte_customers.customer_first_name, ' ', cte_customers.customer_last_name) as customer_name,
            1 as total_customers_ordered,
            count(distinct rent.rental_id) as total_unique_orders,
            count(distinct film.film_id) as total_films_rented,
            sum(payment.payment_amount) as total_revenue
        from cte_rentals as rent
        left join cte_payment as payment
            on rent.rental_id = payment.payment_rental_id
                left join cte_inventory as inv
                    on rent.rental_inventory_id = inv.inventory_id
                        left join cte_film as film
                            on inv.inventory_film_id = film.film_id
                                left join cte_customers
                                    on rent.rental_customer_id = cte_customers.customer_id
                                        left join cte_address
                                            on cte_customers.customer_address_id=cte_address.address_id
                                                left join cte_city
                                                    on cte_address.address_city_id=cte_city.city_id
                                                        left join cte_country
                                                            on cte_city.city_country_id=cte_country.country_id
                                                
        where film.film_title not in ('GOODFELLAS SALUTE')
        group by cte_customers.customer_id, customer_name,city,country
    )

    , cte_final as (
        select
        cte_lifetime_revenue.country,
        cte_lifetime_revenue.city,
        cte_lifetime_revenue.customer_id,
        cte_lifetime_revenue.customer_name,
        cte_customer_lifespan.first_rent,
        cte_customer_lifespan.last_rent,
        case when cte_customer_lifespan.customer_lifespan >= 10 then 'Loyal'
            when cte_customer_lifespan.customer_lifespan >= 4  then 'Regular'
            else 'New'
        end as customer_segment,
        cte_customer_recency.recency,
        total_customers_ordered,
        cte_lifetime_revenue.total_unique_orders,
        cte_lifetime_revenue.total_films_rented,
        cte_lifetime_revenue.total_revenue,
        cte_lifetime_revenue.total_revenue / nullif(cte_lifetime_revenue.total_unique_orders, 0) as average_rental_value,
        case when cte_customer_lifespan.customer_lifespan = 0 then cte_lifetime_revenue.total_revenue
            else cte_lifetime_revenue.total_revenue / cte_customer_lifespan.customer_lifespan
        end as average_monthly_revenue
    from cte_lifetime_revenue
    inner join cte_customer_lifespan
        on cte_lifetime_revenue.customer_id = cte_customer_lifespan.customer_id
            inner join cte_customer_recency
                on cte_lifetime_revenue.customer_id = cte_customer_recency.customer_id
    )

    select * from cte_final
    order by customer_id;

    /* Checking totals */
    
    /*
    select 
    sum(total_customers_ordered) as overall_customers,  
    sum(total_unique_orders) as overall_orders,     
    sum(total_revenue) as overall_revenue    
    from cte_final
    */

    /*
    -----------------------------------------------------------------------------------------------------
    PS: One row per customer showing lifetime metrics, segment, and recency.
        Used as a dimension table in Tableau, related to rep_rental_details via customer_id.
    -----------------------------------------------------------------------------------------------------
    */
