    with cte_rentals as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`
    )

    ,   cte_customers as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_customer`
    )

    ,cte_inventory as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_inventory`
    )

    ,cte_film as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_film`
    )   

    ,cte_film_category as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_film_category`
    )

    ,cte_category as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_category`
    )
    ,cte_payment as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_payment`
    )

select

    rental.rental_id,
    cast(rental.rental_rental_date as date) as rental_date,
    customer.customer_id,
    concat(customer.customer_first_name, ' ', customer.customer_last_name) as customer_name,
    film.film_id,
    film.film_title,
    category.category_id,
    category.category_name,
    coalesce(payment.payment_amount,0) as total_revenue

from cte_rentals as rental
left join cte_payment as payment  
    on rental.rental_id=payment.payment_rental_id
        left join cte_inventory as inventory  
            on rental.rental_inventory_id=inventory.inventory_id
                left join cte_film as film 
                    on inventory.inventory_film_id=film.film_id
                        left join cte_film_category as film_category 
                            on film.film_id=film_category.film_category_film_id
                                left join cte_category as category  
                                    on film_category.film_category_category_id=category.category_id
                                        left join cte_customers as customer 
                                            on rental.rental_customer_id=customer.customer_id

where film.film_title not in ('GOODFELLAS SALUTE')

order by rental.rental_rental_date desc, rental.rental_id;

/*
PS: This is a rental fact table where one row per rental transaction that includes both film id & customer id
*/
