 
    with cte_rentals as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`

  )

  , cte_reporting_dates as (

      select * 
      from `project-401f4646-3663-4125-aaa.reporting_db.reporting_periods_table`
      where reporting_period in ('Day','Month','Year') and reporting_date >= '2015-01-01'

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

  , cte_customers as (

      select *
      from `project-401f4646-3663-4125-aaa.staging_db.stg_customer`
  )

  ,  cte_revenue_per_period as (

      select
          cte_customers.customer_id,
          'Day' as reporting_period,
          date_trunc(cast(rent.rental_rental_date as date), day) as reporting_date,
          sum(payment_amount) as total_revenue
      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
                  left join cte_customers 
                    on rent.rental_customer_id=cte_customers.customer_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by cte_customers.customer_id,reporting_period,reporting_date

      union all

      select
          cte_customers.customer_id,
          'Month' as reporting_period,
          date_trunc(cast(rent.rental_rental_date as date), month) as reporting_date,
          sum(payment_amount) as total_revenue
      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
                  left join cte_customers 
                    on rent.rental_customer_id=cte_customers.customer_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by cte_customers.customer_id,reporting_period,reporting_date

      union all

      select
          cte_customers.customer_id,
          'Year' as reporting_period,
          date_trunc(cast(rent.rental_rental_date as date), year) as reporting_date,
          sum(payment_amount) as total_revenue
      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
                  left join cte_customers 
                    on rent.rental_customer_id=cte_customers.customer_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by cte_customers.customer_id,reporting_period,reporting_date

  )

 ,  cte_final as (

      select
          cte_revenue_per_period.customer_id, 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.total_revenue as total_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date
      where cte_reporting_dates.reporting_period = 'Day'

      union all

      select 
          cte_revenue_per_period.customer_id,
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.total_revenue as total_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date 
      where cte_reporting_dates.reporting_period = 'Month'

      union all

      select 
          cte_revenue_per_period.customer_id,
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.total_revenue as total_revenue
      from cte_reporting_dates inner join cte_revenue_per_period 
        on cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date 
      where cte_reporting_dates.reporting_period = 'Year'

 )

  select * from cte_final
  order by customer_id, reporting_period ,reporting_date ;

